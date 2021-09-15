3.1.11 (2019-04-XX)
===================
* Fix multiple tag selection wizard step.
* Change the required permission for the checkout info link from
  document check in to document checkout details view.
* Lower the log severity when links don't resolve.
* Add DOCUMENTS_HASH_BLOCK_SIZE to control the size of the file
  block when calculating a document's checksum.

3.1.10 (2019-04-04)
===================
* Backport test case improvements from the development branch. Add random
  primary key mixin. Split test case code into mixins. Make the view test
  case and the API test cases part of the same class hierarchy. Update tests
  that failed due to the new import locations.
* Add support for disabling the content type checking test case mixin.
* Update document indexing tests to be order agnostic. GitLab issue #559.
* Add test for the advanced search API.
* Apply merge !36 by Simeon Walker (@simeon-walker) to fix the advanced search
  API.
* Apply merge !35 by Manoel Brunnen (@mbru) to fix building the Docker image
  on the armv7l platform (RasperryPi, Odroid XU4, Odroid HC2). Also fixes
  assertion errors from pip (https://github.com/pypa/pip/issues/6197).
* Apply merge !37 by Roger Hunwicks (@roger.hunwicks) to allow
  TestViewTestCaseMixin to work with a custom ROOT_URLCONF. GitLab issue #566.
* Apply merge !40 by Roger Hunwicks (@/roger.hunwicks) to pin the Tornado
  version used to 6.0 and continue supporting Python 2.7. GitLab issue #568.
* Apply merge !41 by Jorge E. Gomez (@jorgeegomez) to fix the compressed class
  method name. GitLab issue #572.
* Remove notification badge AJAX setup. Individual link AJAX workers are
  obsolete now that the menu is being rendered by its own AJAX renderer.
  GitLab issue #562.
* Add support for server side link badges.
* Add API to list all templates.
* Remove newlines from the rendered templates.
* Reject emails attachments of size 0. Thanks to Robert Schoeftner
  (@robert.schoeftner)for the report and solution. GitLab issue #574.
* Add missing document index API view create permission.
* Fix index list API view. Add index create, delete, detail API tests.
  GitLab issue #564. Thanks to the Stéphane (@shoyu) for the report and debug
  information.
* Validate the state completion value before saving. Thanks to Manoel Brunnen
  (@mbru) for the report and debug information. GitLab issue #557.
* Add the MIMETYPE_FILE_READ_SIZE setting to limit the number of bytes read
  to determine the MIME type of a new document.
* Force object to text when raising PermissionDenied to avoid
  UnicodeDecodeError. Thanks to Mathias Behrle (@mbehrle) for the report
  and the debug information. GitLab issue #576.
* Add support for skipping a default set of tests.

3.1.9 (2018-11-01)
==================
* Convert the furl instance to text to allow serializing it into
  JSON to be passed as arguments to the background task.

3.1.8 (2018-10-31)
==================
* Reorganize documentation into topics and chapters.
* Add Workflows and API chapters.
* Add new material from the Wiki to the documentation.
* Add data migrations to the sources app migraton 0019 to ensure all labels
  are unique before performing the schema migations.
* Add improvements to the metadata URL encoding and decoding to support
  ampersand characters as part of the metadata value. GitLab issue
  #529. Thanks to Mark Maglana @relaxdiego for the report.
* Add custom validator for multiple emails in a single text field.
  Change the widget of the email fields in the mailer app to avoid
  browser side email validation. Closes GitLab issue #530.
  Thanks to Mark Maglana @relaxdiego for the report.
* Add configuration option to change the project/installation URL.
  This is used in the password reset emails and in the default
  document mailing templates.
* Increase the size of the workflow preview image.
* Center the workflow preview image.
* Move the noop OCR backend to the right place.
* Add new management command to display the current configuration
  settings.
* Default the YAML flow format to False which never uses inline.
* Add support for reindexing documents when their base properties like
  the label and description are edited.

3.1.7 (2018-10-14)
==================
* Fix an issue with some browsers not firing the .load event on cached
  images. Ref: http://api.jquery.com/load-event/
* Remove duplicate YAML loading of environment variables.
* Don't load development apps if they are already loaded.
* Make sure all key used as input for the cache key hash are
  bytes and not unicode. GitLab issue #520. Thanks to TheOneValen
  @TheOneValen for the report.
* Ignore document stub from the index mirror. GitLab issue
  #520. Thanks to TheOneValen @TheOneValen for the report.
* Fix for the Docker image INSTALL_FLAG path. Thanks to
  Mark Maglana @relaxdiego for the report and to Hamish Farroq @farroq_HAM
  for the patch. GitLab issue #525.
* Fix the typo in the Docker variable for worker concurrency. Thanks to
  Mark Maglana @relaxdiego for the report and to Hamish Farroq @farroq_HAM
  for the patch. GitLab issue #527.
* Add a noop OCR backend that disables OCR and the check for the
  Tesseract OCR binaries. Set the OCR_BACKEND setting or MAYAN_OCR_BACKEND
  environment variable to ocr.backends.pyocr.PyOCR to use this.
* All tests pass on Python 3.
* documentation: Add Docker installation method using a dedicated
  Docker network.
* documentation: Add scaling up chapter.
* documentation: Add S3 storage configuration section.

3.1.6 (2018-10-09)
==================
* Improve index mirroring value clean up code to remove the spaces at the
  starts and at the end of directories. Closes again GitLab issue #520
  Thanks to TheOneValen @ for the report.
* Improve index mirroring cache class to use the hash of the keys
  instead of the literal keys. Avoid warning about invalid key
  characters. Closes GitLab issue #518. Thanks to TheOneValen @ for the
  report.
* Only render the Template API view for authenticated users.
  Thanks rgarcia for the report.
* Add icon to the cabinet "Add new level" link.
* Display the cabinet "Add new level" link in the top level view too.

3.1.5 (2018-10-08)
==================
* Consolidate some document indexing test code into a new mixin.
* Split the code of the mountindex command to be able to add tests.
* Fix the way the children of IndexInstanceNode are accessed. Fixes GitLab
  issue #518. Thanks to TheOneValen @TheOneValen for the report.
* Remove newlines from the index name levels before using them as FUSE
  directories.
* Fixed duplicated FUSE directory removal.
* Add link and view to show the parsed content of each document page.
* Add a modelform for adding and editing transformation and perform YAML
  validation of arguments.
* Add stricted error checking to the crop transformation.
* Update compressed files class module to work with Python 3.
* Update document parsing app tests to work with Python 3.
* Handle office files in explicit binary mode for Python 3.
* Return a proper list of SearchModel instances (Python 3).
* Specify FUSE literals in explicit octal notation (Python 3).
* URL quote the encoded names of the staging files using Django's compat
  module. (Python 3)
* Open staging file in explicit binary mode. (Python 3)
* Add separate Python 2 and Python 3 versions of the MetadataType model
  .comma_splitter() static method.
* Update the metadata app tests to work on Python 3.
* Make sure metadata lookup choices are a list to be able to add the
  optional marker (Python 3).
* Make sure the image in the document preview view is centered when it is
  smaller than the viewport.
* Restore use of the .store_body variable accidentally remove in
  63a77d0235ffef3cd49924ba280879313c622682. Closes GitLab issue #519.
  Thanks to TheOneValen @TheOneValen for the report.
* Add shared cache class and add mounted index cache invalidation when
  document and index instance nodes are updated or deleted.
* Fix document metadata app view error when adding multiple optional
  metadata types. Closes GitLab issue #521. Thanks to the TheOneValen
  @TheOneValen for the report.

3.1.4 (2018-10-04)
==================
* Fix the link to the documenation. Closes GitLab issue #516.
  Thanks to Matthias Urlichs @smurfix for the report.
* Update related links. Add links to the new Wiki and Forum.
* Add Redis config entries in the Docker images to disable
  saving the database and to only provision 1 database.
* Remove use of hard coded font icon for document page
  rendering busy indicator.
* Disable the fancybox caption link if the document is
  in the trash.
* Load the DropZone CSS from package and remove the
  hard code CSS from appearance/base.css.
* Add support for indexing on OCR content changes.
* Add support for reindexing document on content parsing
  changes.
* Strip HTML entities from the browser's window title.
  Closes GitLab issue #517. Thanks to Daniel Carrico @daniel1113
  for the report.
* Improve search app. Refactored to resolve search queries
  by terms first then by field.
* Add explanation to the launch workflows tool.

3.1.3 (2018-09-27)
==================
* Make sure template API renders in non US languages.
* Fix user groups view.
* Add no results help text to the document type -> metadata type
  association view.
* Expose the Django INSTALLED_APPS setting.
* Add support for changing the concurrency of the Celery workers in the
  Docker image. Add environment variables MAYAN_WORKER_FAST_CONCURRENCY,
  MAYAN_WORKER_MEDIUM_CONCURRENCY and MAYAN_WORKER_SLOW_CONCURRENCY.
* Add latest translation updates.
* Fixes a few text typos.
* Documentation updates in the deployment and docker chapters.

3.1.2 (2018-09-21)
==================
* Database access in data migrations defaults to the 'default' database.
  Force it to the user selected database instead.
* Don't use a hardcoded database alias for the destination of the database
  conversion.
* Improve natural key support in the UserOptions model.
* Update from Django 1.11.11 to 1.11.15.
* Add support to the convertdb command to operate on specified apps too.
* Add test mixin to test the db conversion (dumping and loading) of a specific app.
* Add an user test mixin to group user testing.
* Add test the user managament app for database conversion.
* Add support for natural keys to the DocumentPageImageCache model.
* Add database conversion test to the common app.
* Fix label display for resolved smart links when not using a dynamic label.
* Only show smart link resolution errors to the user with the smart link edit
  permission.
* Intercept document list view exception and display them as an error message.

3.1.1 (2018-09-18)
==================
* CSS tweak to make sure the AJAX spinner stays in place.
* Fix 90, 180 and 270 degrees rotation transformations.

3.1 (2018-09-17)
================
- Improve database vendor migration support
- Add convertdb management command.
- Add error checking to the crop transformation arguments.
- Update dropzone.js' timeout from 30 seconds to 120 to allow upload
  of large files on slow connections.
- Increase gunicorn's timeout from 30 seconds to 120.
- Update packages versions: Pillow:5.2.0, PyYAML:3.13, django-environ:0.4.5,
  django-model-utils:3.1.2, django-mptt:0.9.1, django-widget-tweaks: 1.4.2,
  flanker:0.9.0, flex:6.13.2, furl:1.2, gevent:1.3.5, graphviz: 0.8.4,
  gunicorn:19.9.0, pyocr:0.5.2, python-dateutil:2.7.3
- Remove use of django-compressor and cssmin now that the project used
  Whitenoise.
- Display error when attempting to recalculate the page count of an empty
  document (document stub that has no document version).
- Add support for client side caching of document page images. The time
  the images are cached is controlled by the new setting
  DOCUMENTS_PAGE_IMAGE_CACHE_TIME which defaults to 31556926 seconds (1 year).
- The document quick label selection field now uses a select2 widget.
- Include querystring when force reload of a bare template view.
- Speed up document image fade in reveal.
- Use reseteable timer to ensure more document panels heights are matched.
- Rewrote Mayan's JavaScript suite MayanApp into ECMAScript2015.
- Remove use is waitForJQuery.
- Remove code statistics from the documentation.
- Remove the pending work chapter. This is now available in the Wiki:
  wiki.mayan-edms.com
- Unify template title rendering.
- Add support for template subtitles.
- Make sure the on entry action of the initial state of workflows
  executes on document creation.
- Add new document app events: document type created and document type
  edited.
- Add link to document type events.
- Add new metadata app events: metadata type created, metadata type edited,
  metadata type to document type relationship update.
- Add link to metadata type events.
- Add support for subscribing to metadata type events.
- Add link to view the events of a tag.
- Add support for subscribing to the events of a tag.
- Add the tag events view permissions to the tag model ACL.
- Hide the title link of documents in the trash.
- Add support for document metadata events: add, edit and remove.
- Add workflow action to update the label and description of a document.
- Add COMMON_PROJECT_TITLE as a setting option to customize the title
  string.
- Add support for YAML configuration files.
- Add support for editing setting options and saving them using the
  new YAML configuration file support.
- Add new revertsettings management command.
- Add new permission to edit setting via the UI.
- Renamed setting LOCK_MANAGER_DEFAULT_BACKEND to LOCK_MANAGER_BACKEND.
- Add help texts to more setting options.
- Add ACL support for metadata types.
- Add cascade permission checks for links. Avoid allowing users
  to reach a empty views because they don't access to any of
  the view's objects.
- Apply link permission cascade checks to the message of the day,
  indexing and parsing, setup link.
- Add ACL support to the message of the day app.
- The index rebuild permission can now be set as part of the index
  ACL for each individual index.
- Add cascade permission check to the index rebuild tool link.
- The index rebuild tool now responds with the number of indexes
  queued to rebuild instead of a static acknowledment.
- Add missing permission check to the document duplicate scan
  link.
- Add new document indexing permission. This permission allows
  user to view an index instance as opposed to the current
  permission which allows viewing an index definiton on the
  setup menu.
- Add support to conditionally disable menus.
- Disable the Tags menu when the user doesn't have the
  tag create permission or the tag view access for any tag.
- Disable the Cabinets menu when the user doesn't have the
  cabinet create permission or the cabinet view permission
  for any cabinet.
- Update forum link in the about menu.
- Only show the settings namespace list link where it is
  relevant.
- Add support for the fillcolor argument to the rotate
  transformation.
- Sort documents by label.
- Add recently added document list view. The setting
  DOCUMENTS_RECENT_COUNT has been renamed to
  DOCUMENTS_RECENT_ACCESS_COUNT. New setting
  DOCUMENTS_RECENT_ADDED_COUNT added.
- Use platform independant hashing for transformations.
- Add support to the ObjectActionMixin to report on instance action
  failures. Add also an error_message class property and the new
  ActionError exception.
- Add favorite documents per user. Adds new setting option
  DOCUMENTS_FAVORITE_COUNT.
- Add new class based dashboard widget. This new widget supports
  subclassing and is template based. All exising widgets have been
  converted. ACL filtering was added to the widget results.
- In addition to the document view permission, the checkout detail
  view permission is now needed to view the list of checked out
  document.
- After queuing a chart for update, the view will now redirect
  to the same chart.
- The multiple document action dropdown is now sorted alphabetically.
- Improve statistics subclassing. Split class module into classes
  and renderers.
- Sort facet link, object, secondady and sidebar actions.
- Add support for extended templates when there are no results.
- Add help messages and useful links to several apps when there
  are no results available.
- Add a new column to settings showing if they are overrided
  via environment variable.
- The official config filename is config.yml.
- Interpret ALLOWED_HOSTS as YAML.
- Don't show the document types of an index instance.
- Add the tag created and tag edited events.
- Add support for blocking the changing of password for specify users.
- Add support for changing the HOME_VIEW, LOGIN_URL and LOGIN_REDIRECT_URL
  from the settings view.
- Instead of the document content view, the document type parsing setup
  permissions is now required to view the parsing error list.
- The document type parsing setup permission can now be granted for
  individual document types.
- Add link to view a specific page's OCR content.
- Remove the duplicated setting pdftotext_path from the OCR path.
  This is now handled by the document parsing app.
- Implement partial refresh of the main menu.
- Remove usage of pace.js. Would cause XMLRequest to fallback to
  synchronous mode.
- Add custom AJAX spinner.
- Complete refactor of the compress archive class support. Closes
  GitLab issue #7.
- Add support for preserving the extension of document files when
  using the quick label feature. Added to the document properties
  edit view and the document upload view. Closes GitLab issue
  #360.
- Add new dashboard item to display the total page count.
- Show the document type being uploaded in the source view title.
- Setting SOURCE_SCANIMAGE_PATH is now SOURCES_SCANIMAGE_PATH.
- Refactor the staging file image generation to support
  background task generation, caching and cache sharing.
- New queue: sources_fast. Used for staging file generation.
- New settings: SOURCES_STAGING_FILE_CACHE_STORAGE_BACKEND and
  SOURCES_STAGING_FILE_CACHE_STORAGE_BACKEND_ARGUMENTS to control
  where and how staging file caching is done.
- Fix an edge case on the document indexing where an empty
  node could be left behind.
- Improve the speed of the document indexing.
- Move the matchHeight call from lazy loading to image loading.
  Reduces the chance of wrongly sized cards.
- Generalize the JavaScript menu rendering into an API for
  templates that only refresh the menu when there are changes.
  Closes GitLab issue #511. Thanks to Daniel Carrico
  @daniel1113 for the report.
- Refactor the ModelAttribute class into two separate classes:
  ModelAttribute for executable model attributes and ModelField
  for actual ORM fields.
- Expose more document fields for use in smart links.
- The size of the document type label field has been increased
  from 32 to 96 characters.
- Add file_size and datetime fields to the DocumentPageCachedImage
  model.
- Make icon classes file template based.
- Add the current step and total steps of a wizard in the template context.

3.0.3 (2018-08-17)
==================
- Tags app: Add explicit casting of escaped tag labels to prevent exploit
  of cross site scripting. Thanks to Lokesh (@lokesh1095) for
  the report and proposed solutions. Closes GitLab issue #496.
- Tags app: Add explicit post action redirect for the tag attach and
  tag remove actions when working on a single document.

3.0.2 (2018-08-16)
==================
- Docker install script: Default to verbose.
- Docker install script: Increase startup timer to 10 seconds.
- Docker install script: Allow configuring the PostgreSQL port.
- Documentation: Add deployment step that configures Redis to discard
  unused task data when it runs out of memory.
- Index app: Add natural key support to the Index model.
- Mailer app: Add natural key support to the mailer app.
- Cabinets: Redirect to the cabinet list view after creating a new cabinet.
- Builds: Limit the number of branches that trigger the full test suit.
- Converter app: Fix crop transformation argument parsing.
- Converter app: Add error checking to the crop transformation arguments.
  Thanks to Jordan Wages (@wagesj45) for the report and investigation on the issue.
  Closes GitLab issue #490
- Common app: Fix post login redirection to honor the ?next= URL query string
  argument. Thanks go to K.C. Wong (@dvusboy1). Closes GitLab
  issue #489.
- Docker install script: Detect if Docker installed and provide help
  text if not.
- Sources app: Update dropzone.js' timeout from 30 seconds to 120 to allow
  upload of large files on slow connections.
- Documentation: Increase gunicorn's timeout from 30 seconds to 120.
- Documents app: Display error when attempting to recalculate the page
  count of an empty
  document (document stub that has no document version).
- Appearance app: Include querystring when force reload of a bare template view.
- Documents app: Fix trashed document count and document page count swapped
  dashboard icons.
- Documents app: Rename the multi document download link from "Download" to
  "Advanced download" for consistency.
- Documentation: Remove code statistics from the documentation.
- Documentation: Remove the pending work chapter. This is now available in
  the Wiki: wiki.mayan-edms.com
- Appearance app: Add support for hiding a links icon. Hide all object menu
  links' icons.
- Documents app: Hide the title link of documents in the trash.
- Workflow app: Define a redirection after workflow actions are edited.
- Appearance app: avoid setting window.location directly to avoid exploit
  of cross site scripting. Thanks to Lokesh (@lokesh1095) for the report
  and solution. Closes GitLab issue #494.
- Cabinets app: Escape cabinet labels to avoid possible exploit of
  cross site scripting. Thanks to Lokesh (@lokesh1095) for the report
  and proposed solutions. Closes GitLab issue #495.
- Language translation synchonization.

3.0.1 (2018-07-08)
==================
- Pin javascript libraries to specific versions to avoid using
  potentianlly broken updates automatically. GitLab issue #486.
- French and Polish language translation updates.
- Merge request #25. Thanks to Daniel Albert @esclear
  for the patch.

3.0 (2018-06-29)
================
- Rename the role groups link label from "Members" to "Groups".
- Rename the group users link label from "Members" to "Users".
- Don't show full document version label in the heading of the document
  version list view.
- Show the number of pages of a document and of document versions in
  the document list view and document versions list views respectively.
- Display a document version's thumbnail before other attributes.
- User Django's provided form for setting an users password.
  This change allows displaying the current password policies
  and validation.
- Add method to modify a group's role membership from the group's
  view.
- Rename the group user count column label from "Members" to "Users".
- Backport support for global and object event notification.
  GitLab issue #262.
- Remove Vagrant section of the document. Anything related to
  Vagrant has been move into its own repository at:
  https://gitlab.com/mayan-edms/mayan-edms-vagrant
- Add view to show list of events performed by an user.
- Allow filtering an event list by clicking on the user column.
- Display a proper message in the document type metadata type relationship
  view when there are no metadata types exist.
- Require the document view permission to view trashed documents.
- Make the multi object form perform an auto submit when the value is changed.
- Improved styling and interaction of the multiple object action form.
- Add checkbox to allow selecting all item in the item list view.
- Revise and improve permission requirements for the documents app API.
- Downloading a document version now requires the document download permission
  instead of just the document view permission.
- Creating a new document no longer works by having the document create
  permission in a global manner. It is now possible to create a document via
  the API by having the document permission for a specific document type.
- Viewing the version list of a document now required the document version
  view permission instead of the document view permission.
- Not having the document version view permission for a document will not
  return a 403 error. Instead a blank response will be returned.
- Reverting a document via API will new require the document version revert
  permission instead of the document edit permission.
- Fix permission filtering when performing document page searching.
- Fix cabinet detail view pagination.
- Update project to work with Django 1.11.11.
- Fix deprecations in preparation for Django 2.0.
- Improve permission handling in the workflow app.
- The checkedout detail view permission is now required for the checked out document detail API view.
- Switch to a resource and service based API from previous app based one.
- Add missing services for the checkout API.
- Fix existing checkout APIs.
- Update API vies and serializers for the latest Django REST framework version. Replace DRF Swagger with DRF-YASG.
- Update to the latest version of Pillow, django-activity-stream, django-compressor, django-cors-headers,
  django-formtools, django-qsstats-magic, django-stronghold, django-suit, furl, graphviz, pyocr,
  python-dateutil, python-magic, pytz, sh.
- Update to the latest version the packages for building, development, documentation and testing.
- Add statistics script to produce a report of the views, APIs and test for each app.
- Merge base64 filename patch from Cornelius Ludmann.
- SearchModel retrun interface changed. The class no longer returns the result_set value. Use the queryset returned instead.
- Update to Font Awesome 5.
- Turn Mayan EDMS into a single page app.
- Split base.js into mayan_app.js, mayan_image.js, partial_navigation.js.
- Add a HOME_VIEW setting. Use it for the default view to be loaded.
- Fix bug in document page view. Was storing the URL and the querystring as a single url variable.
- Use history.back instead of history.go(-1).
- Don't use the previous variable when canceling a form action. Form now use only javascript's history.back().
- Add template and modal to display server side errors.
- Remove the unused scrollable_content internal feature.
- Remove unused animate.css package.
- Add page loading indicator.
- Add periodic AJAX workers to update the value of the notifications link.
- Add notification count inside a badge on the notification link.
- Add the MERC specifying javascript library usage.
- Documents without at least a version are not scanned for duplicates.
- Use a SHA256 hex digest of the secret key at the name of the lockfile. This makes the generation of the name repeatable while unique between installations.
- Squashed apps migrations.
- Convert document thumbnails, preview, image preview and staging files to template base widgets.
- Unify all document widgets.
- Display resolution settings are now specified as width and height and not a single resolution value.
- Printed pages are now full width.
- Move the invalid document markup to a separate HTML template.
- Update to Fancybox 3.
- Update to jQuery 3.3.1
- Move transfomations to their own module.
- Split documents.tests.test_views into base.py, test_deleted_document_views.py,
  test_document_page_views.py, test_document_type_views.py, test_document_version_views.py,
  test_document_views.py, test_duplicated_document_views.py
- Sort smart links by label.
- Rename the internal name of the document type permissions namespace. Existing permissions will need to be updated.
- Add support for OR type searches. Use the "OR" string between the terms. Example: term1 OR term2.
- Removed redundant permissions checks.
- Move the page count display to the top of the image.
- Unify the way to gather the project's metadata. Use mayan.__XX__ and a new common tag named {% project_information '' %}
- Return to the same source view after uploading a document.
- Add new WizardStep class to decouple the wizard step configuration.
- Add support for deregister upload wizard steps.
- Add wizard step to insert the document being uploaded to a cabinet.
- Fix documentation formatting.
- Add upload wizard step chapte.
- Improve and add additional diagrams.
- Change documenation theme to rtd.
- Fix carousel item height issues.
- Add the "to=" keyword argument to all ForeignKey, ManayToMany and OneToOne Fields.
- Add Makefile target to check the format of the README.rst file.
- Mark the feature to detect and fix the orientatin of PDF as experimental.
- Don't show documents with 0 duplicates in the duplicated document list.
- Clean up the duplicated document model after a document is deleted.
- Add support for roles ACLs.
- Add support for users ACLs.
- Add support for groups ACLs.
- Sort permission namespaces and permissions in the role permission views.
- Invert the columns in the ACL detail view.
- Fix issue #454. Thanks to Andrei Korostelev @kindkaktus for the issue and the
  solution.
- Update the role permission edit view require the permission grant or permission
  revoke permissions for the selected role.
- Only show the new document link if the user has access to create documents of
  at least one document type. GitLab Issue #302. Thanks to kg @kgraves.
- Support passing arguments to the document, document cache and document signatures
  storage backends. New settings: DOCUMENTS_STORAGE_BACKEND_ARGUMENTS,
  DOCUMENTS_CACHE_STORAGE_BACKEND_ARGUMENTS, SIGNATURES_STORAGE_BACKEND_ARGUMENTS
- Remove the setting STORAGE_FILESTORAGE_LOCATION. Document storage
  location for the storage.backend.filebasedstorage.FileBasedStorage
  backdend must now passed via the DOCUMENTS_STORAGE_BACKEND_ARGUMENTS,
  DOCUMENTS_CACHE_STORAGE_BACKEND_ARGUMENTS, or
  SIGNATURES_STORAGE_BACKEND_ARGUMENTS if the backend is used to documents,
  the document image cache and/or document signatures. Use
  DOCUMENTS_STORAGE_BACKEND_ARGUMENTS = '{ location: <specific_path> }'
  If no path is specified the backend will default to
  'mayan/media/document_storage'.
- Standardize the way storages are used. All apps that use storage now define
  their storages in the .storages modules instead of the .runtime module.
  The storage.backends.filebasedstorage.FileBasedStorage has been remove,
  instead Django's default storage is used and each app is responsible
  of specifying their default path.
- Unify checkbox selection code for list items and table items.
- Add smart checkbox manager.
- Update Chart.js version.
- Improve line chart appearance. Fix mouse hover label issue.
- Add JavaScript dependency manager.
- Add support for passing arguments to the OCR backend.
- Fix issue when using workflows transitions with the new version
  upload event as trigger. Thanks to Sema @Miggaten for the find and
  the solution.
- Removing running workflow instances in document of a specific type if
  that document type is removed from the workflow.
- Make error messages persistent and increase the timeout of warning to 10 seconds.
- Improve rendering of the details form.
- Update rendering of the readonly multiselect widget to conform to Django's updated field class interface.
- Add warning when using SQLite as the database backend.
- Use Mailgun's flanker library to process the email sources.
- Add locking for interval sources. This reduces the chance of repeated documents from long running email downloads.
- Add the option to enable or disable parsing when uploading a document for each document type.
- Add a new setting option to enable automatic parsing for each new document type created.
- Add support for HTML bodies to the user mailers.
- Production ALLOWED_HOSTS settings now defaults to a safer ['127.0.0.1', 'localhost', '[::1]']
- Capture menu resolution errors on invalid URLs. Closes GitLab issue #420.
- New environment variables: MAYAN_SECRET_KEY, MAYAN_CELERY_ALWAYS_EAGER, MAYAN_CELERY_RESULT_BACKEND,
  MAYAN_BROKER_URL, MAYAN_DATABASE_ENGINE, MAYAN_DATABASE_CONN_MAX_AGE, MAYAN_DATABASE_NAME,
  MAYAN_DATABASE_USER, MAYAN_DATABASE_PASSWORD, MAYAN_DATABASE_HOST, MAYAN_DATABASE_PORT,
  MAYAN_DEBUG.
- Stricter defaults. CELERY_ALWAYS_EAGER to False, ALLOWED_HOSTS to ['127.0.0.1', 'localhost', '[::1]'].
- New initialization command. Creates media/system and populates the SECRET_KEY and VERSION files.
- Sane scanner source paper source now defaults to blank.
- Merge Docker image creation back into the main repository.
- Docker image now uses gunicorn and whitenoise instead of NGINX to server the app and
  the static media.
- All installation artifact are now created and read from the media folder.
- Debian is now the Linux distribution used for the Docker image.
- Most Docker Celery workers are now execute using a lower OS priority number.
- Add COMMON_PRODUCTION_ERROR_LOGGING setting to control the logging of errors in production. Defaults to False.
- Change the error log file handle class to RotatingFileHandle to avoid an indefinitely growing log file.
- Disable embedded signatute verification during the perform upgrade command.
- Replace the DOCUMENTS_LANGUAGE_CHOICES setting option. Replaced with the new DOCUMENTS_LANGUAGE_CODES.
- Fix error when trying to upload a document from and email account with 'from' and 'subject' metadata.
- Fix typo on message.header get from 'Suject' to 'Subject'.
- On multi part emails keep the original From and Subject properties for all subsequent parts if the sub parts don't specify them. Fixes issue #481. Thanks to Robert Schöftner @robert.schoeftner for the report and debug information.
- Don't provide a default for the scanner source adf_mode. Some scanners throw an error even when the selection
  if supported.
- Add a "Quick Download" action to reduce the number of steps to download a single document. GitLab issue #338.
- Recalculate a document's indexes when attaching or removing a tag from or to it.
- Recalculate all of a tag's documents when a tag is about to be deleted.
