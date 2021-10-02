[![pypi][pypi]][pypi-url]
![python][python]
![license][license]
[![Docker pulls](https://img.shields.io/docker/pulls/mayanedms/mayanedms.svg?maxAge=3600)](https://hub.docker.com/r/mayanedms/mayanedms/)
[![Docker Stars](https://img.shields.io/docker/stars/mayanedms/mayanedms.svg?maxAge=3600)](https://hub.docker.com/r/mayanedms/mayanedms/)
[![Commits][commits]][commits-url]
[![Support][support]][support-url]
[![Store](https://img.shields.io/badge/Online_store-black)](https://teespring.com/stores/mayan-edms)
[![Donation](https://img.shields.io/badge/donation-PayPal-brightgreen)](https://paypal.me/MayanEDMS)


[pypi]: https://img.shields.io/pypi/v/mayan-edms.svg
[pypi-url]: https://pypi.org/project/mayan-edms/

[builds]: https://gitlab.com/mayan-edms/mayan-edms/badges/master/build.svg
[builds-url]: https://gitlab.com/mayan-edms/mayan-edms/pipelines

[python]: https://img.shields.io/pypi/pyversions/mayan-edms.svg
[python-url]: https://img.shields.io/pypi/l/mayan-edms.svg?style=flat

[license]: https://img.shields.io/pypi/l/mayan-edms.svg?style=flat
[license-url]: https://gitlab.com/mayan-edms/mayan-edms/blob/master/LICENSE

[commits]:  https://img.shields.io/github/commit-activity/y/mayan-edms/mayan-edms.svg
[commits-url]: https://gitlab.com/mayan-edms/mayan-edms/

[support]: https://img.shields.io/badge/Get_support-brightgreen
[support-url]: https://www.mayan-edms.com/support/

<h3 align="center"> Documentation specific to HAMMER's iteration of the repository is located near the end of the README. </h3>
<div align="center">
  <a href="http://www.mayan-edms.com">
    <img width="200" heigth="200" src="https://gitlab.com/mayan-edms/mayan-edms/raw/master/docs/_static/mayan_logo.png">
  </a>
  <br>
  <br>
  <p>
    Mayan EDMS is a document management system. Its main purpose is to store,
    introspect, and categorize files, with a strong emphasis on preserving the
    contextual and business information of documents. It can also OCR, preview,
    label, sign, send, and receive thoses files. Other features of interest
    are its workflow system, role based access control, and REST API.
  <p>


</div>

<h2 align="center">Book</h2>

The final version of the book "Exploring Mayan EDMS" available now!

<p align="center">
    <a href="https://sellfy.com/p/um2fkx/">
        <img width="400" src="https://d12swbtw719y4s.cloudfront.net/images/v6RpxW40/aP0qKLjkPiAuXZhYuB45/wDAULAzFyx.jpeg?w=548">
    </a>
</p>

The link is https://sellfy.com/p/um2fkx/

<h2 align="center">Installation</h2>

The easiest way to use Mayan EDMS is by using the official
[Docker](https://www.docker.com/) image. Make sure Docker is properly installed
and working before attempting to install Mayan EDMS.

For the complete set of installation instructions visit the Mayan EDMS documentation
at: https://docs.mayan-edms.com/parts/installation.html

<h2 align="center">Hardware requirements</h2>

- 2 Gigabytes of RAM (1 Gigabyte if OCR is turned off).
- Multiple core CPU (64 bit, faster than 1 GHz recommended).

<h2 align="center">Important links</h2>


- [Homepage](http://www.mayan-edms.com)
- [Documentation](https://docs.mayan-edms.com)
- [Contributing](https://gitlab.com/mayan-edms/mayan-edms/blob/master/CONTRIBUTING.md)
- [Forum](https://forum.mayan-edms.com/)
- [Source code, issues, bugs](https://gitlab.com/mayan-edms/mayan-edms)
- [Plug-ins, other related projects](https://gitlab.com/mayan-edms/)
- [Translations](https://www.transifex.com/rosarior/mayan-edms/)
- [Videos](https://www.youtube.com/channel/UCJOOXHP1MJ9lVA7d8ZTlHPw)

<h2 align="center">Additional Documentation</h2>
Our group chose feature two. We created a form for reviewers to enter and score candidates along various directions, which can be saved and aggregated across multiple reviewers. Out of the three options given, we thought this option had company-candidate interaction, and it was the most essential point out of the three to have. We updated the existing Mayan framework to reflect our purposes.

The form is simplified so there is a minimal number of categories that still cover all the applicant information. The simplicity increases the reviewer's efficiency and is easy to understand and use. Additionally, the design only uses two colors to emphasize the answer fields so users can easily find focus and maintain it while working.

<h3>Initial Design</h3>
We created an initial design on <a href="https://www.figma.com/file/fjZ7zQ3fFLX0zpS3pslCfZ/hammer?node-id=312%3A2"> Figma </a> to create an outline/wireframe for the coding process.

<img width="450" alt="Screen Shot 2021-10-01 at 10 07 46 PM" src="https://user-images.githubusercontent.com/70723676/135700554-7e2a8ff9-349b-4c10-a29a-fd89f563e160.png">

<h3>Final Form</h3>
How to use (user/reviewer):

- Note down the applicant ID corresponding to the resume
- Enter reviewer first and last name
- Rate applicant's quality of education, work, extracurriculars, and skills and awards from 1-5, 1 being poor quality and 5 being great quality
- (Optional) Leave any additional comments in the last blank
- Save the form to save information to backend

<img width="1439" alt="Screen Shot 2021-10-01 at 4 50 00 AM" src="https://user-images.githubusercontent.com/70723676/135700748-4667e28f-b030-4010-8eaf-1185e3d01d8c.png"><img width="1439" alt="Screen Shot 2021-10-01 at 4 50 08 AM" src="https://user-images.githubusercontent.com/70723676/135700936-c00835ca-b290-4af4-b5a2-3d5e09e3a629.png">

<h3>Testing for Devs</h3>

- Manual testing instructions are located <a href="https://docs.google.com/document/d/1RwBCOA6BSgwzwmiDnEcmgtD0O8u6Ak4VweT3pv_eBE8/edit?usp=sharing"> here </a> 
- CI testing is located at <a href="https://github.com/CMU-313/fall-2021-hw2-hammer/blob/master/.github/workflow/build.yml">.github/workflows/build.yml</a>



