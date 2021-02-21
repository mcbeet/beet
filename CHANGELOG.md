# Changelog

<!--next-version-placeholder-->

## v0.9.2 (2021-02-21)
### Fix
* Annotate descriptors ([`4e47cc6`](https://github.com/vberlier/beet/commit/4e47cc6dc612eb0f804dc8f24454f5f590a24544))

## v0.9.1 (2021-02-20)
### Fix
* Make it possible to specify an existing cache and use run_beet in examples ([`5cdea1d`](https://github.com/vberlier/beet/commit/5cdea1d46d36a4324582232a6773edefcadb4350))

## v0.9.0 (2021-02-20)
### Feature
* Add run_beet helper function ([`a2cb545`](https://github.com/vberlier/beet/commit/a2cb5454972f768b215248fbc95575fd26a34dfc))

## v0.8.2 (2021-02-20)
### Fix
* Overload merge to automatically merge pack extras too ([`a586ee3`](https://github.com/vberlier/beet/commit/a586ee30eb00aadb0276a6bb7b2c4b2a637ed236))

## v0.8.1 (2021-02-18)
### Fix
* Add FormattedPipelineException and use config_error_handler in subproject ([`49895e3`](https://github.com/vberlier/beet/commit/49895e34246f39529dd984cec434863977be5da8))

## v0.8.0 (2021-02-18)
### Feature
* Remove __render__ and expose render path and render group in meta ([`adc9452`](https://github.com/vberlier/beet/commit/adc945207098bdf4eed7699cd01a855ad899e846))
* Add ctx.override to temporarily change meta ([`c1483d0`](https://github.com/vberlier/beet/commit/c1483d08244ed159f055d18ab487191b40a49cde))
* Expose renderer as a standalone plugin ([`e935383`](https://github.com/vberlier/beet/commit/e935383abf7f8de9db0a7ce354b50fa78eca45fb))
* Add sandbox ([`bd538af`](https://github.com/vberlier/beet/commit/bd538af938b740c07a1f1bdf6834816f4c476e51))
* Add explicit activate context manager ([`1e21f66`](https://github.com/vberlier/beet/commit/1e21f66fa8068cc7309951f9924dce85ab27b333))

### Fix
* Replace exception_fallthrough with PipelineFallthroughException ([`35ace13`](https://github.com/vberlier/beet/commit/35ace13821338f699a3426858c3b2257fbf2e73e))
* Set ctx template global in __post_init__ ([`96d928b`](https://github.com/vberlier/beet/commit/96d928b6a81f1f272930b2ed30eac082ff455e66))
* Expose the template directories ([`7d6f7a1`](https://github.com/vberlier/beet/commit/7d6f7a1b009770984515b09550bc36e0c7b39d96))
* Ignore cache relative to the resolved directory ([`3e77d79`](https://github.com/vberlier/beet/commit/3e77d7929b5c2c3b71c994f52b19e2dccafbdbff))

### Documentation
* Document ctx.activate() and ctx.override() ([`286eca2`](https://github.com/vberlier/beet/commit/286eca20b7d5b0ab64ff74048f0f8c1ecaef5e2e))

## v0.7.0 (2021-02-16)
### Feature
* Add lantern_load plugin ([`7118f10`](https://github.com/vberlier/beet/commit/7118f10f49e574b8701004fdcc5f30dc56e89167))

## v0.6.1 (2021-02-13)
### Fix
* Make it possible to use text components and override the description in plugins ([`ad972d0`](https://github.com/vberlier/beet/commit/ad972d011f10e7006d34c07a37f8116f7bc2227f))

## v0.6.0 (2021-02-13)
### Feature
* Add subproject helper ([`d604179`](https://github.com/vberlier/beet/commit/d60417924b44284dac45d5ad4b23d4b5a08aee99))

### Documentation
* Add link to pipeline configuration video ([`811d426`](https://github.com/vberlier/beet/commit/811d426ebe5943b683e957a2e98e97a8522b3122))
* Add docstring to context inject method ([`2f09ffe`](https://github.com/vberlier/beet/commit/2f09ffe591612246c23d8997467630aa79002c75))

## v0.5.1 (2021-01-27)
### Fix
* Expose project metadata in context ([`a04081c`](https://github.com/vberlier/beet/commit/a04081ce23c941bd240ff1187fc40645fce7e627))
* Better dotted pack name handling ([`79fccff`](https://github.com/vberlier/beet/commit/79fccfff9d92353cebbdc631b6ae56b2e6a99be3))

## v0.5.0 (2021-01-23)
### Feature
* Add beet.contrib.minify_functions plugin ([`a7774a9`](https://github.com/vberlier/beet/commit/a7774a9b799eac7eceb078759e02b8714da9d9c1))
* Add beet.contrib.minify_json plugin ([`78cd972`](https://github.com/vberlier/beet/commit/78cd9728401570ad772a3684577667c126eef0a9))

### Fix
* Typo in serialization descriptor ([`edbe174`](https://github.com/vberlier/beet/commit/edbe1740bd9bb0b85877746f693f3ba7247bbf57))

### Documentation
* Add link to plugins basics video ([`3d7a3db`](https://github.com/vberlier/beet/commit/3d7a3dbceefeb4afc998a2599f02c441016c8c31))

## v0.4.0 (2021-01-14)
### Feature
* Handle resource pack fonts and tweak docstrings ([`57cce73`](https://github.com/vberlier/beet/commit/57cce7380a2f9b9a15a61bac4d824e2d6ce48a2f))
* Add shaders ([`34505d9`](https://github.com/vberlier/beet/commit/34505d99e9b6714c593a4a5f5b919d22dacd6fa2))
* Locate_minecraft() now takes into account the MINECRAFT_PATH environment variable ([`ad6668b`](https://github.com/vberlier/beet/commit/ad6668b639a8ed6eba18cff1a41b11666b2db488))

### Fix
* Also look for the .minecraft folder in the launcher files on linux ([`5645789`](https://github.com/vberlier/beet/commit/564578935b25193a2cbbcf8e71f44d942336a5b7))
* Strip extra underscores from normalized name ([`55b8494`](https://github.com/vberlier/beet/commit/55b8494248098aa532fa816b0abdf6d46b236021))

## v0.3.3 (2021-01-10)
### Fix
* Tweak typing for merge implementation ([`8efa444`](https://github.com/vberlier/beet/commit/8efa444ccf67dd25eb1fd23d4e89f07407bf404c))

### Documentation
* Add link to library overview video ([`4f37a74`](https://github.com/vberlier/beet/commit/4f37a7496d863b0535b39a1b6c1ad3df786bc89b))

## v0.3.2 (2020-12-29)
### Fix
* Use forward slash for zipfile paths on windows ([`b605c07`](https://github.com/vberlier/beet/commit/b605c07a06106fd97866b9c442b39313381aabb5))

### Documentation
* Link to command-line video ([`1f45b03`](https://github.com/vberlier/beet/commit/1f45b036c55902d1736f1f63cc26202291f29842))
* Add quick start to readme ([`3310d16`](https://github.com/vberlier/beet/commit/3310d16d5490c9554c40acb0c4d295b4d8e10e68))

## v0.3.1 (2020-12-22)
### Fix
* Default match shouldn't match anything ([`6f01d6a`](https://github.com/vberlier/beet/commit/6f01d6a19d63d9374e575942cf40dc1b14a4df88))

## v0.3.0 (2020-12-22)
### Feature
* Add function_header plugin ([`bb73eee`](https://github.com/vberlier/beet/commit/bb73eeef0d984ca80cfd378ab2b0a99d89a33d47))

### Fix
* Rename inline plugins ([`a6b7aaa`](https://github.com/vberlier/beet/commit/a6b7aaa60d97bf203d771861effc0ee61425786d))

### Documentation
* Add module docstring to inline plugins ([`d829d89`](https://github.com/vberlier/beet/commit/d829d89c815c15b34dd51ac6e3a68d563906b3c4))

## v0.2.2 (2020-12-21)
### Fix
* Trigger release to update readme ([`d409af5`](https://github.com/vberlier/beet/commit/d409af56d4c82da5d3c2743a158128cb4ed0b062))

### Documentation
* Start writing docs ([`034c662`](https://github.com/vberlier/beet/commit/034c662878c88d2da84c71f15d46e85c38e2e5db))
* Update readme ([`58c9822`](https://github.com/vberlier/beet/commit/58c98226b091f3dd5994888bfdd71301dafb278f))
* Add mudkip ([`fb3cfdd`](https://github.com/vberlier/beet/commit/fb3cfddee1b220e055659393e9ce747fddcd5a26))

## v0.2.1 (2020-12-21)
### Fix
* Include better dependencies for windows ([`b28977f`](https://github.com/vberlier/beet/commit/b28977f206bd48b0cdae67ac1dad2e17ade81f24))

### Documentation
* Fix main branch ([`74ac998`](https://github.com/vberlier/beet/commit/74ac998c7103ebdb9c95058e141ab1acc703670b))

## v0.2.0 (2020-12-21)
### Feature
* Trigger first automatic release ([`a5664b3`](https://github.com/vberlier/beet/commit/a5664b3fa7f7fc6c9d1d93f1cc26f91504dd3dae))
