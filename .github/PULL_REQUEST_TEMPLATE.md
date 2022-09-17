## Repository contributions to the PyBitmessage project

### Code

- Try to refer to github issue tracker or other permanent sources of discussion about the issue.
- It is clear from the diff *what* you have done, it may be less clear *why* you have done it so explain why this change is necessary rather than what it does.

### Documentation

Use `tox -e py27-doc` to build a local copy of the documentation.

### Tests

- If there has been a change to the code, there's a good possibility there should be a corresponding change to the tests
- To run tests locally use `tox` or `./run-tests-in-docker.sh`

## Translations

- For helping with translations, please use [Transifex](https://www.transifex.com/bitmessage-project/pybitmessage/).
- There is no need to submit pull requests for translations.
- For translating technical terms it is recommended to consult the [Microsoft Language Portal](https://www.microsoft.com/Language/en-US/Default.aspx).

### Gitiquette

- Make the pull request against the ["v0.6" branch](https://github.com/Bitmessage/PyBitmessage/tree/v0.6)
- PGP-sign the commits included in the pull request
- Use references to tickets, e.g. `addresses #123` or `fixes #234` in your commit messages
- Try to use a good editor that removes trailing whitespace, highlights potential python issues and uses unix line endings
- If for some reason you don't want to use github, you can submit the patch using Bitmessage to the "bitmessage" chan, or to one of the developers.

