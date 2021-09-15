2.0.2 (2016-02-09)
==================
- Install testing dependencies when installing development dependencies.
- Fix GitLab issue #250 "Empty optional lookup metadata trigger validation error".
- Fix OCR API test.
- Move metadata form value validation to .clean() method.
- Only extract validation error messages from ValidationError exception instances.
- Don't store empty metadata value if the update checkbox is not checked.
- Add 2 second delay to document version tests to workaround MySQL limitation.
- Strip HTML tags from the browser title.
- Remove Docker and Docker Compose files.

2.0.1 (2016-01-22)
==================
- Fix GitLab issue #243, "System allows a user to skip entering values for a required metadata field while uploading a new document"
- Fix GitLab issue #245, "Add multiple metadata not possible"
- Updated Vagrantfile to provision a production box too.

2.0 (2015-12-04)
================

- New source homepage: https://gitlab.com/mayan-edms/mayan-edms
- Update to Django 1.7
- New Bootstrap Frontend UI
- Easier theming and rebranding
- Improved page navigation interface
- Menu reorganization
- Removal of famfam icon set
- Improved document preview generation
- Document submission for OCR changed to POST
- New YAML based settings system
- Removal of auto admin creation as separate app
- Removal of dependencies
- ACL system refactor
- Object access control inheritance
- Removal of anonymous user support
- Metadata validators refactor
- Trash can support
- Retention policies
- Support for sharing indexes as FUSE filesystems
- Clickable preview images titles
- Removal of eval
- Smarter OCR, per page parsing or OCR fallback
- Improve failure tolerance (not all Operational Errors are critical now)
- RGB tags
- Default document type and default document source
- Link unbinding
- Statistics refactor
- Apps merge
- New signals
- Test improvements
- Indexes recalculation after document creation too
- Upgrade command
- OCR data moved to ocr app from documents app
- New internal document creation workflow return a document stub
- Auto console debug logging during development and info during production
- New class based and menu based navigation system
- New class based transformations
- Usage of Font Awesome icons set
- Management command to remove obsolete permissions: `purgepermissions`
- Normalization of 'title' and 'name' fields to 'label'
- Improved API, now at version 1
- Invert page title/project name order in browser title
- Django's class based views pagination
- Reduction of text strings
- Removal of the CombinedSource class
- Removal of default class ACLs
- Removal of the ImageMagick and GraphicsMagick converter backends
- Remove support for applying roles to new users automatically
- Removal of the DOCUMENT_RESTRICTIONS_OVERRIDE permission
- Removed the page_label field


1.1.1 (2015-05-21)
==================

- Update to Django 1.6.11
- Fix make_dist.sh script
- Add test for issue #163
- Activate tests for the sources app
- Removal of the registration app
- New simplified official project description
- Improvements to the index admin interface
- Removal of installation statistics gathering
- Remove unused folder tag
- Fix usage of ugettext to ugettext_lazy
- Increase size of the lock name field
- New style documentation


1.1 (2015-02-10)
================

- Uses Celery for background tasks
- Removal of the splash screen
- Adds a home view with common function buttons
- Support for sending and receiving documents via email
- Removed custom logging app in favor of django-actvity-stream
- Adds watch folders
- Includes Vagrant file for unified development and testing environments
- Per user locale profile (language and timezone)
- Includes news document workflow app
- Optional and required metadata types
- Improved testings. Automated tests against SQLite, MySQL, PostgreSQL
- Many new REST API endpoints added
- Simplified text messages
- Improved method for custom settings
- Addition of CORS support to the REST API
- Per document language setting instead of per installation language setting
- Metadata validation and parsing support
- Start of code updates towards Python 3 support
- Simplified UI
- Stable PDF previews generation
- More technical documentation


1.0 (2014-08-27)
================

- New home @ https://github.com/mayan-edms/mayan-edms
- Updated to use Django 1.6
- Translation updates
- Custom model properties removal
- Source code improvements
- Removal of included 3rd party modules
- Automatic testing and code coverage check
- Update of required modules and libraries versions
- Database connection leaks fixes
- Support for deletion of detached signatures
- Removal of Fabric based installations script
- Pluggable OCR backends
- OCR improvements
- License change, Mayan EDMS in now licensed under the Apache 2.0 License
- PyPI package, Mayan EDMS in now available on PyPI: https://pypi.python.org/pypi/mayan-edms/
- New REST API
