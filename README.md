Easy API for sending e-mails based on Python's built-in smtplib and email modules.  
  
## Example Usage  

```python
from email_for_humans import Email, EmailClient  


# Note: EMAIL and EMAIL_AUTH refer to hypothetical environment variables
# NEVER hard-code your auth in your code!
email_client = EmailClient(login=EMAIL, password=EMAIL_AUTH,
                           host='smtp.office365.com', port=587)

msg = Email(from_addr=email_client.login,
            to_addr="an_email_address@domain.com",
            subject="Sample Subject Line",
            body="Here's the body of the e-mail.",
            cc="another_email_address@domain.com")

msg.add_attachment(b"Test bytes", "test_file.csv")
msg.add_attachment_from_path(path="/some/path/file.ext")

email_client.send(msg)
```

## Multiple Recipients
Multiple recipients are possible using a list or a string with recipients separated by commas. E.g. change the to_addr param in the Email object above to: `"an_email_address@domain.com, another_email_address@domain.com"`. Use the same syntax for multiple Cc's.
