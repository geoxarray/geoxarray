# Releasing Geoxarray

1. checkout main branch
2. pull from repo
3. run the unittests
4. run `loghub` and update the `CHANGELOG.md` file:

   ```
   loghub geoxarray/geoxarray --token $LOGHUB_GITHUB_TOKEN -st $(git tag --sort=-version:refname --list 'v*' | head -n 1) -plg bug "Bugs fixed" -plg enhancement "Features added" -plg documentation "Documentation changes" -plg backwards-incompatibility "Backward incompatible changes" -plg refactor "Refactoring"
   ```

Don't forget to commit!

5. Create a tag with the new version number, starting with a 'v', eg:

```
git tag -a v0.22.45 -m "Version 0.22.45"
```

See [semver.org](http://semver.org/) on how to write a version number.

6. push changes to github `git push --follow-tags`
7. Verify github action tests passed
8. Create github release
9. Verify deploy github workflow passes and package deployed to PyPI
