"""Easy API for sending e-mails based on smtplib and email.

Example:

    >>> from simple_email import Email, EmailClient
    >>>
    >>> # Note: EMAIL and EMAIL_AUTH refer to hypothetical environment variables
    >>> # NEVER hard-code your auth in your code!
    >>> email_client = EmailClient(login=EMAIL, password=EMAIL_AUTH,
                                   host='smtp.office365.com', port=587)
    >>>
    >>> msg = Email(from_addr=email_client.login,
                    to_addr="an_email_address@domain.com",
                    subject="Sample Subject Line",
                    body="Here's the body of the e-mail.",
                    cc="another_email_address@domain.com")
    >>>
    >>> msg.add_attachment(b"Test bytes", "test_file.csv")
    >>> msg.add_attachment_from_path(path="/some/path/file.ext")
    >>>
    >>> email_client.send(msg)

"""
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.encoders import encode_base64
from mimetypes import guess_type
from pathlib import Path
from typing import List, Tuple, Union


def parse_email_addr(email: str) -> str:
    """Strips surrounding angle brackets from an e-mail address."""
    if '<' in email:
        data = email.split('<')
        email = data[1].split('>')[0].strip()
    return email.strip()


def path_to_bytes(path: str) -> bytes:
    """Helper function to get a bytes object from the contents of a file on disk.

    Args:
        path: Path to a file to import as a bytes object.

    Returns:
        File contents loaded from path as bytes in memory.

    """
    with open(path, 'rb') as f:
        data = f.read()

    return data


def path_to_attachment_components(path: str) -> Tuple:
    """Helper function to get a file's bytes and metadata for use with Email.add_attachment.

    Args:
        path: Path to a file to import as a bytes object.

    Returns:
        Tuple of args needed to create an attachment to an Email.

    """
    ctype, encoding = guess_type(path)
    maintype, subtype = ctype.split('/', 1)
    data = path_to_bytes(path, project)
    file_name = Path(path).name

    return data, file_name, maintype, subtype


class EmailClient:
    """Email client that will be used to send  and receive e-mails.

    Example:
        >>> # `config` below refers to a hypothetical env file.
        >>> email_client = EmailClient(login=config.EMAIL, password=config.EMAIL_AUTH,
                                       host='smtp.office365.com', port=587)

    """

    def __init__(self, login: str, password: str, host: str, port: int):
        """Instatiate the credentials for the e-mail client without authenticating.

        Args:
            login: The e-mail address used to log in with your e-mail provider.
                   E.g. 'an_email_address@domain.com'
            password: The password associated with the login. For security, it is strongly recommended
                      that this parameter be fed from an environment variable and NOT in plain text.
            host: The smtp host name. E.g. 'smtp.office365.com' for Outlook365.
            port: host's port. E.g. 587 for Outlook365.

        """
        self.login = login
        self.password = password
        self.host = host
        self.port = port

    def send(self, msg, from_addr=None, to_addrs=None, mail_options=(), rcpt_options=()):
        """Send an Email object as an e-mail.

        Args:
            msg: Ideally an Email object. May also be a string of ASCII characters or a byte string.
            from_addr: An RFC 822 from-address string.
            to_addrs: A list of RFC 822 to-address strings.
            mail_options: A list of ESMTP options (such as 8bitmime) to be used in MAIL FROM commands.
            rcpt_options: ESMTP options (such as DSN commands) that should be used with all RCPT commands.

        Note:
            See https://docs.python.org/3/library/smtplib.html#smtplib.SMTP.sendmail
            for more information on acceptable args.

        Returns:
            A dictionary, with one entry for each recipient that was refused.
            Each entry contains a tuple of the SMTP error code and the accompanying error message sent by the server.

        Example:
            >>> email_client.send(msg)

        """
        with smtplib.SMTP(host=self.host, port=self.port) as server:
            server.starttls()
            server.login(self.login, self.password)

            from_addr = from_addr if from_addr is not None else msg.email['From']
            to_emails = list(filter(None, msg.email['To'].split(',') + msg.email['Cc'].split(',')))
            to_addrs = [parse_email_addr(complete_email) for complete_email in to_emails]
            msg = str(msg)

            return server.sendmail(from_addr=from_addr, to_addrs=to_addrs, msg=msg,
                                   mail_options=mail_options, rcpt_options=rcpt_options)


class Email:
    """Formatted e-mail object to be used with EmailClient.send.

    Example:
        >>> msg = Email(from_addr=email_client.login,
                        to_addr="an_email_address@domain.com",
                        subject="Sample Subject Line",
                        body="Here's the body of the e-mail.",
                        cc="another_email_address@domain.com")
        >>>
        >>> msg.add_attachment(b"Test bytes", "test_file.csv")
        >>> msg.add_attachment_from_path(path="/some/path/file.ext")

    """

    def __init__(self, from_addr: str, to_addr: Union[str, List], subject: str, body: str,
                 body_type: str = 'plain', cc: Union[str, List] = '', body_encoding: str = 'us-ascii'):
        """

        Args:
            from_addr: E-mail address the Email should come from.
            to_addr: E-mail address(es) that will be on the To line of the Email; included in Email recipients.
            subject: Email's subject line.
            body: Text in the body of the e-mail.
            body_type: Sets the type of text in the body. Defaults to 'plain', but can be 'plain' or 'html'.
            cc: E-mail address(es) that will be on the Cc line of the Email; included in Email recipients.
            body_encoding: The encoding of the text in the body. Defaults to 'us-ascii', but can be 'utf-8', etc.

        """
        self.email = MIMEMultipart()
        self.email['Subject'] = subject
        self.email['From'] = from_addr
        self.email['To'] = to_addr if isinstance(to_addr, str) else ", ".join(to_addr)
        self.email['Cc'] = cc if isinstance(cc, str) else ", ".join(cc)

        text = MIMEText(body, body_type, body_encoding)
        self.email.attach(text)

    def add_attachment(self, data: bytes, file_name: str, maintype: str = 'application', subtype: str = 'octet-stream'):
        """Add attachment from bytes object in memory.

        Args:
            data: Desired attachment data as a bytes object.
            file_name: Name of the attached file that recipients will see.
            maintype: Mimetype maintype.
            subtype: Mimetype subtype.

        See Also:
            add_attachment_from_path

        """
        attachment = MIMEBase(maintype, subtype)
        attachment.set_payload(data)
        encode_base64(attachment)
        attachment.add_header('Content-Disposition', 'attachment', filename=file_name)
        self.email.attach(attachment)

    def add_attachment_from_path(self, path: str):
        """Add attachment from path's contents.

        Args:
            path: Path to a file to import as a bytes object.

        See Also:
            add_attachment

        """
        components = path_to_attachment_components(path)
        self.add_attachment(*components)

    def __str__(self):
        return self.email.as_string()
