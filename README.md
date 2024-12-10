# pycolint

Why another commit linter? Because all available tools seemed to do too much,
while lacking either customizability or a sane way to communicate semantics
to the developer.
PyCoLint is a commitlinter written in python.
It's only job is to help you adhere to the syntax defined by the
conventional commit specification[https://www.conventionalcommits.org/en/v1.0.0/].
It does not know anything about the semantics of commit messages.
That means it does not offer any semantics related features.
Instead of having to care about version bumping etc., we want to provide
helpful error messages and other feedback that should help a team to
stick to their conventions.

The linter warns about:

- exceeding maximum line length
- empty scope, e.g., `"feat(): empty scope"`
- missing type
- ending the commit msg hdr with a `.`
- missing separation between body and header
- empty body
- whitespace in scopes

We try to stick close to the official conventional commit specification.
As such we do not restrict the usable types nor the scopes in any way.


### ToDo in order of importance

- [ ] check against a list of user defined types
- [ ] check against a list of user defined scopes 
- [ ] configure via `pyproject.toml`
- [ ] add pre-commit hook
- [ ] warn about past tense for very common cases, e.g., "added", "made", "did",...

### Known Issues

- [ ] only the last token corresponding to an error is marked
- [ ] Unclosed parentheses/missing scope is not detected for this message `"feat(: msg."`
