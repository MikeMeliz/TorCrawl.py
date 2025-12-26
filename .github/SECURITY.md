# Security Policy for TorCrawl.py

## Introduction

**TorCrawl.py** is a Python-based tool designed to crawl websites via the Tor network, ensuring anonymity and privacy. As a user, it is important to follow best security practices when using or contributing to this project to ensure that it operates securely and responsibly.

This document outlines security procedures and best practices for the **TorCrawl.py** project. It provides guidance on how to report security vulnerabilities, as well as how to use the tool securely.

## Reporting Security Vulnerabilities

If you discover a security vulnerability in TorCrawl.py, or a way that TorCrawl.py's users sensitive information are getting leaked while they're using the tool, please report it directly to the project maintainers. 
We take security issues seriously and will respond promptly to mitigate any risks.

#### To report a security vulnerability:

1. Do not open a public issue on GitHub.
2. Open a new [Security Advisory](https://github.com/MikeMeliz/TorCrawl.py/security/advisories/new).
3. Provide detailed information about the vulnerability, including:
   - Description of the issue,
   - Steps to reproduce (if applicable),
   - Suggested fix (if you have one).
4. Keep the issue confidential until we’ve had a chance to investigate and address the vulnerability.

## Security Best Practices for Using TorCrawl.py

#### Protect Your Identity and Privacy

- Always use TorCrawl.py with the Tor network to ensure anonymity while crawling.
- Do not use TorCrawl.py to access websites that could identify you through other means (e.g., logged-in accounts, IP tracking, or cookie tracking).

#### Respect the Robots.txt File

- TorCrawl.py does not automatically respects the robots.txt file of websites. Ensure that the tool is configured to abide by the crawling policies set by the website owner.
- Be considerate when crawling by using rate-limiting to avoid overwhelming the target servers (e.g., `-p 5` to add a 5 seconds pause between requests.

#### Be Aware of Legal and Ethical Considerations

- TorCrawl.py is intended for ethical and lawful use. Always ensure that your activities comply with applicable laws and regulations regarding web scraping and data collection.
- Be mindful of the ethical implications of scraping data from websites, particularly with regard to user privacy and data protection.

#### Avoid Overloading Websites

- TorCrawl.py can be configured to throttle the crawling speed to minimize the impact on the websites being crawled (e.g., `--pause 5`).
- Do not use the tool to overload a website or disrupt its operation. Use the `--pause` option to control the speed and request frequency.

#### Code and Dependencies Security

- TorCrawl.py relies on external libraries and dependencies. Always ensure you are using the latest, stable versions of these dependencies to avoid known security vulnerabilities.
- Keep an eye on security advisories for dependencies like requests, stem, PySocks, and others.
- Review and audit the codebase regularly for security weaknesses and vulnerabilities.

#### Secure Development Practices

- Avoid hardcoding sensitive information (e.g., authentication credentials, API keys) directly into the source code.
- Ensure that any data collected or logged is appropriately sanitized to prevent sensitive information from being exposed.
- Use environment variables or configuration files for managing sensitive data.

#### Community Guidelines

- Respect other people's privacy and do not use the tool for illegal activities, harassment, or scraping sites without permission.
- Follow good ethical standards in how you use TorCrawl.py and contribute to its development.

#### Additional Resources

- [Tor Project](https://www.torproject.org/)
- [OWASP Web Service Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Web_Service_Security_Cheat_Sheet.html)
- [Python Security Best Practices](https://docs.python.org/3/tutorial/)

<hr>

By following the guidelines outlined in this document, you contribute to the security and ethical use of TorCrawl.py.
