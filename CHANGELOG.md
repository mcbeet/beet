# Changelog

<!--next-version-placeholder-->

## v0.50.0 (2022-01-08)
### Feature
* Relay full game log ([`c847840`](https://github.com/mcbeet/beet/commit/c8478407a8ef5cf5d6b91598f07e3a65cccd2635))
* Add config overrides ([`97bf032`](https://github.com/mcbeet/beet/commit/97bf032f39180a3a648726c1025a9306a6f17206))

## v0.49.2 (2022-01-08)
### Fix
* Display server errors ([`bf5cf30`](https://github.com/mcbeet/beet/commit/bf5cf30335bf529504d5b0879ddcc68049d73b98))

## v0.49.1 (2022-01-07)
### Fix
* Ignore unicode errors when reading log file ([`c521b12`](https://github.com/mcbeet/beet/commit/c521b12fd5c584819b719d4dd30e3087f3cfaa8c))

### Documentation
* Add rationale ([`e79e3d3`](https://github.com/mcbeet/beet/commit/e79e3d37ecdbd9b411ba9a912a3e5b8c6892da0d))

## v0.49.0 (2021-12-25)
### Feature
* Automatically figure out the root of the function tree ([`19f21e1`](https://github.com/mcbeet/beet/commit/19f21e10770fa02c2d99c23d43d54443d1e32b08))

### Breaking
* generate_tree no longer accepts the root argument in templates  ([`19f21e1`](https://github.com/mcbeet/beet/commit/19f21e10770fa02c2d99c23d43d54443d1e32b08))

## v0.48.5 (2021-12-25)
### Fix
* Only reload modules that weren't already imported ([`7ba93af`](https://github.com/mcbeet/beet/commit/7ba93af5e5485d17d0401b10f25e473618a5158c))

## v0.48.4 (2021-12-25)
### Fix
* Export TreeData ([`68e8d03`](https://github.com/mcbeet/beet/commit/68e8d03d0fb6f25864904769e2077bda876b27e8))

## v0.48.3 (2021-12-18)
### Fix
* Deprecate hangman ([`24ff3cb`](https://github.com/mcbeet/beet/commit/24ff3cbf055342864afd386e36ea821b590d8ce8))

## v0.48.2 (2021-12-10)
### Fix
* Add namespace option for babelbox ([`fb902fe`](https://github.com/mcbeet/beet/commit/fb902fedb4107105ee183a252f9f07c4a4a18c23))

## v0.48.1 (2021-12-09)
### Fix
* Bump latest pack format to 8 ([`8bbc17e`](https://github.com/mcbeet/beet/commit/8bbc17e39589fcc1e193404c1d5c9bf719300def))

## v0.48.0 (2021-11-30)
### Feature
* Add LinkManager and refactor a bunch of things ([`b76063f`](https://github.com/mcbeet/beet/commit/b76063f89fffbd89a4f1319b24e75b6feafc4d57))

## v0.47.0 (2021-11-29)
### Feature
* Add beet.contrib.livereload and --reload option ([`3d56260`](https://github.com/mcbeet/beet/commit/3d5626005f739c5affd5f4d80a863f7cda61c530))

## v0.46.0 (2021-11-29)
### Feature
* Extract autosave and linking strategy into their own plugins ([`f82a8d5`](https://github.com/mcbeet/beet/commit/f82a8d5f7b353a2c8fc549bb829ea33cd652c203))

### Fix
* Make pydantic work with PurePath ([`7f44324`](https://github.com/mcbeet/beet/commit/7f44324fe09c0aa02fc29c8f477db942fedd113c))
* Forgot deleted caches get immediately reset so no need to remove them from the multicache ([`a4cd64c`](https://github.com/mcbeet/beet/commit/a4cd64cbfdbb59f0e36af71252d63fa79a287237))
* Add cache override ([`071a64a`](https://github.com/mcbeet/beet/commit/071a64a762781e20f08e73e07476172f29cf785a))
* Remove deleted caches from multicache ([`b64603c`](https://github.com/mcbeet/beet/commit/b64603c726d1a0417637c8cc64cac25ab88d6175))

## v0.45.3 (2021-11-27)
### Fix
* Make it possible to not copy the output to the linked world ([`ce10eca`](https://github.com/mcbeet/beet/commit/ce10eca1279de496c4267998f045776feb7aa088))

## v0.45.2 (2021-11-26)
### Fix
* Load files by trying all the possible extensions ([`c437220`](https://github.com/mcbeet/beet/commit/c43722067df063ea6e53cbff41e3db897f64ce4b))

## v0.45.1 (2021-11-26)
### Fix
* Forgot to update require method on context to accept multiple plugins ([`2b0aae8`](https://github.com/mcbeet/beet/commit/2b0aae8c033d72c68bab527e1d2fd7a83902265a))

## v0.45.0 (2021-11-24)
### Feature
* Add beet.contrib.copy_files and beet.contrib.extra_files ([`85b4cee`](https://github.com/mcbeet/beet/commit/85b4ceebe6c46c9f41f8b17288bd324d34becea8))

## v0.44.12 (2021-11-23)
### Fix
* Rename link to logo ([`f8eaaae`](https://github.com/mcbeet/beet/commit/f8eaaae016faf108256c6cdbb1c60fe735e374d8))

## v0.44.11 (2021-11-21)
### Fix
* Accidentally added mudkip to main dependencies oops ([`b96f83f`](https://github.com/mcbeet/beet/commit/b96f83f76f8ab3972e7ea2717ecf9c6c344d0928))

## v0.44.10 (2021-11-20)
### Fix
* Remove fnvhash dependency ([`a298a1b`](https://github.com/mcbeet/beet/commit/a298a1bd534e3b55c8ebfd8f0fed61011e70b0b1))

## v0.44.9 (2021-11-19)
### Fix
* Update `yellow_shulker_box` for 1.18 ([#173](https://github.com/mcbeet/beet/issues/173)) ([`9c0d56c`](https://github.com/mcbeet/beet/commit/9c0d56c0764541329183024c9d5d17c093f5f6ad))

## v0.44.8 (2021-11-15)
### Fix
* Support multiple plugins in a single require call ([`4251abc`](https://github.com/mcbeet/beet/commit/4251abc6e6b8e5effb4dea6b0d3519c49549fb8e))

## v0.44.7 (2021-11-08)
### Fix
* Use beet.contrib.load to handle the load option ([`c23e4ad`](https://github.com/mcbeet/beet/commit/c23e4ad0ed10e3480255dc7fc4a6e7a0f1c826b3))
* Make beet.contrib.load work with absolute paths ([`4971c40`](https://github.com/mcbeet/beet/commit/4971c40259e5c67ece20d82c47566f2fe6ce7af3))

## v0.44.6 (2021-11-08)
### Fix
* Make it possible to load packs manually ([`81fee16`](https://github.com/mcbeet/beet/commit/81fee160f9dfbba6d43463c260cbcffba04baca3))

## v0.44.5 (2021-11-05)
### Fix
* Turn discard into invalidate_changes ([`9c38d86`](https://github.com/mcbeet/beet/commit/9c38d86c8e6fa9c9cc886edd117fc441790bd8f7))

## v0.44.4 (2021-11-05)
### Fix
* Add helper to easily remove files from the cache ([`9f6dca0`](https://github.com/mcbeet/beet/commit/9f6dca053515ca421f59a917013c0b98147ccb0d))

## v0.44.3 (2021-11-05)
### Fix
* Put message retrieval logic into MessageManager ([`0f187f2`](https://github.com/mcbeet/beet/commit/0f187f23d0a76d1f0b73697c706cf36d7453c5a4))

## v0.44.2 (2021-11-05)
### Fix
* Cleanup empty containers and namespaces after merge ([`43b7d08`](https://github.com/mcbeet/beet/commit/43b7d086b5347c80a189ec6f9234cb73f50625ab))

## v0.44.1 (2021-11-05)
### Fix
* Missing return type for resolve_scope_map() ([`1968f50`](https://github.com/mcbeet/beet/commit/1968f504a14c2332421583973dfeb71305ece401))

## v0.44.0 (2021-11-05)
### Feature
* Add beet.contrib.messages ([`d623640`](https://github.com/mcbeet/beet/commit/d623640ee5e711a9aecefa44889301f30db36f30))

### Fix
* Add snake_case utility ([`8009226`](https://github.com/mcbeet/beet/commit/8009226dc9437b57529c2efcc14696fe1c34c145))
* Rename GlyphSizes and true_type_fonts ([`718b36b`](https://github.com/mcbeet/beet/commit/718b36b152faa68bfa46ab4debb83e47e13c7bc3))

## v0.43.3 (2021-10-23)
### Fix
* Tweak draft again ([`dfc3524`](https://github.com/mcbeet/beet/commit/dfc35247c08bb6fe52b4c3c480e9fcb937892c43))

## v0.43.2 (2021-10-23)
### Fix
* Tweak log_time, draft API, cache formatting, and add Pack.configure ([`2dca46d`](https://github.com/mcbeet/beet/commit/2dca46d759ea7b315a5dfa81ad7100d426ff56fa))

## v0.43.1 (2021-10-22)
### Fix
* Dbg display name for objectives generated with `generate_objective()` ([`f8669c5`](https://github.com/mcbeet/beet/commit/f8669c595cb4f6c6165648ec54426e234409d7e8))

## v0.43.0 (2021-10-22)
### Feature
* Add draft class ([`d501db1`](https://github.com/mcbeet/beet/commit/d501db1689d7d2df8a25a2d239e65e935f9bfb11))
* Add generator draft ([`1e341c5`](https://github.com/mcbeet/beet/commit/1e341c511fd9eb6bb5f6242e9d52202141ba12d2))

## v0.42.2 (2021-10-22)
### Fix
* Align line numbers and tweak dbg formatting ([`715ee23`](https://github.com/mcbeet/beet/commit/715ee2366b65e458da400903b36bfd567a8b20d1))

## v0.42.1 (2021-10-21)
### Fix
* Show source preview in dbg ([`51b2625`](https://github.com/mcbeet/beet/commit/51b2625ae6ca27bd9dc3009a9447bd0f01b1d421))

## v0.42.0 (2021-10-21)
### Feature
* Add beet.contrib.dbg ([`a908790`](https://github.com/mcbeet/beet/commit/a908790c53555433c7b14c74a6c409962fc3b23d))

## v0.41.11 (2021-10-21)
### Fix
* Add discord link ([`7fd0887`](https://github.com/mcbeet/beet/commit/7fd0887da00ded7c37f9dbe643462ad05deb37a2))

## v0.41.10 (2021-10-20)
### Fix
* Log timings ([`b01c9ab`](https://github.com/mcbeet/beet/commit/b01c9ab3c82fd01f29cce364b92b2615fd4e83cf))

## v0.41.9 (2021-10-18)
### Fix
* Use "extra" logging parameter instead of hijacking args ([`5cca927`](https://github.com/mcbeet/beet/commit/5cca92774ce61215662b9e99772a29b1400cffa2))

## v0.41.8 (2021-10-14)
### Fix
* Add GameEventTag ([`ab6ba24`](https://github.com/mcbeet/beet/commit/ab6ba2405dfdddc45a0ad7a6fe9dd761bd08b3f0))

## v0.41.7 (2021-10-09)
### Fix
* Use percent formatting with logger ([`c3d5d72`](https://github.com/mcbeet/beet/commit/c3d5d72da1a9675783369b732b6c1464467f66c0))
* Switch to debug level for logging downloads and cache expiration ([`d3ff227`](https://github.com/mcbeet/beet/commit/d3ff22788d65e8aec076dae8f0c788aa39b41ebd))
* Add missing annotation for DictReader ([`9cf24c9`](https://github.com/mcbeet/beet/commit/9cf24c96d5600d1cc4cbbaef567b6e80d22d3912))

## v0.41.6 (2021-09-26)
### Fix
* Make it possible to log with a custom prefix ([`8577f9b`](https://github.com/mcbeet/beet/commit/8577f9b40048c0871b3d8d24c6c97b5de16f002f))

## v0.41.5 (2021-09-26)
### Fix
* Insert newline between logs and final error ([`ed52132`](https://github.com/mcbeet/beet/commit/ed5213229dc4346aaf622a440b547a5c2e89f7d1))

## v0.41.4 (2021-09-25)
### Fix
* Allow key normalization for core containers ([`cdd273a`](https://github.com/mcbeet/beet/commit/cdd273a242f326d8b7caf47ecc715e69c1d4a85e))

## v0.41.3 (2021-09-25)
### Fix
* Handle multiline logs ([`f68e4a6`](https://github.com/mcbeet/beet/commit/f68e4a6c26fbafda14952afe7a3a1f0f9089a128))

## v0.41.2 (2021-09-13)
### Fix
* Make file instances hashable based on their runtime ids ([`c696466`](https://github.com/mcbeet/beet/commit/c696466df9308c6625a8532ca390a82ad94af3e5))

## v0.41.1 (2021-09-11)
### Fix
* Provide the required_field utility ([`f5cbf9c`](https://github.com/mcbeet/beet/commit/f5cbf9c0fb22f47f6d14001b50c72bf839752c68))

## v0.41.0 (2021-09-08)
### Feature
* **hangman:** Add run sequentially ([`b918e6e`](https://github.com/mcbeet/beet/commit/b918e6e0a166e01e02f851acd9c74a77b600a929))

## v0.40.1 (2021-09-01)
### Fix
* Output pack after the exit phase of autoload plugins ([`e6871cb`](https://github.com/mcbeet/beet/commit/e6871cb69c95f00d2e9851bf0c641ebed43c9fbe))
* **docs:** Forgot to update on_bind in overview ([`6962f3b`](https://github.com/mcbeet/beet/commit/6962f3b3353f62b62db1c5e981f93ed2b7f44301))

## v0.40.0 (2021-09-01)
### Feature
* Add merge policy ([`ff4e104`](https://github.com/mcbeet/beet/commit/ff4e104adf78c00436d9a3a3139aaf1a3f8ba510))
* Add beet.contrib.auto_yaml ([`f505b8b`](https://github.com/mcbeet/beet/commit/f505b8be69aaddba380354d84d35f6e0d6f45de3))

### Fix
* Update dependencies and deal with pyright delusions ([`be9ed6a`](https://github.com/mcbeet/beet/commit/be9ed6a894fed82597559909778b8aff88eb6789))

## v0.39.0 (2021-08-22)
### Feature
* Expose resolved schemas ([`35a7800`](https://github.com/mcbeet/beet/commit/35a7800189d842fd904b4055fadd8ebf6dc879d7))

## v0.38.0 (2021-08-17)
### Feature
* Handle strings and iterables when appending or prepending to functions ([`c8d2795`](https://github.com/mcbeet/beet/commit/c8d2795b1589b8f7e0d025da02b3577d12f4afcf))

## v0.37.0 (2021-08-16)
### Feature
* Add pack extensions and walk method ([`dc7bf85`](https://github.com/mcbeet/beet/commit/dc7bf85cfc40d500dfb7e8c0e8cea1470e6f70e0))
* Add core yaml file ([`8e109e4`](https://github.com/mcbeet/beet/commit/8e109e4b7244a0ea83318651bc2a2d53f372e8c4))

## v0.36.0 (2021-07-09)
### Feature
* Handle wildcards in config when loading packs ([`2cf1181`](https://github.com/mcbeet/beet/commit/2cf1181ebccce2782ee5e072e6eeb8bb29331679))

## v0.35.1 (2021-07-05)
### Fix
* **format_json:** Make pydantic keep int values for indent option ([`ef0169f`](https://github.com/mcbeet/beet/commit/ef0169fe2957feda11dece7a07bcda9d7aed3973))

## v0.35.0 (2021-07-05)
### Feature
* Plugin "project_advancement" ([`160ec91`](https://github.com/mcbeet/beet/commit/160ec918ab1a600742a19ddb8b09ae23fd81265c))

## v0.34.1 (2021-07-01)
### Fix
* Coerce plugin options to concrete types ([`dd2de5a`](https://github.com/mcbeet/beet/commit/dd2de5a10c01f8e8dd6ef59072879751c3f7a3e8))

## v0.34.0 (2021-06-29)
### Feature
* Add configurable decorator to load and validate plugin options ([`a3a39fe`](https://github.com/mcbeet/beet/commit/a3a39fe2cc6668b8e098b6bb597f3febb35119a1))
* Add ctx.validate() ([`e1210cf`](https://github.com/mcbeet/beet/commit/e1210cf287127e08abccd3040f9ef602d1392485))
* Add stable_int_hash() utility ([`e08d004`](https://github.com/mcbeet/beet/commit/e08d004d818652d6301f885171ebef9cfaa2875e))

## v0.33.0 (2021-06-26)
### Feature
* Add beet.contrib.load_yaml plugin ([`86af226`](https://github.com/mcbeet/beet/commit/86af2264faa9f9484896fbe925e9d61def648186))
* Make it possible to pass a custom callback to ensure_serialized() and ensure_deserialized() ([`d75648b`](https://github.com/mcbeet/beet/commit/d75648b9f23cd66e87b79dd663370f8288291cd3))

## v0.32.1 (2021-06-23)
### Fix
* Show template filename in traceback ([`695fab6`](https://github.com/mcbeet/beet/commit/695fab62cea3e0a3c2dd53128d2769e40fc998ff))

## v0.32.0 (2021-06-18)
### Feature
* Make pillow optional ([`9778883`](https://github.com/mcbeet/beet/commit/977888375b0ca3ca334a391b0ab4bc4a1ed9a0d5))

## v0.31.4 (2021-06-15)
### Fix
* Separate normalized project id into its own context attribute ([`1487fcf`](https://github.com/mcbeet/beet/commit/1487fcf0bb08411d7095fa30d96ac9cbe2164ca8))

## v0.31.3 (2021-06-11)
### Fix
* Support named nested commands ([`d209774`](https://github.com/mcbeet/beet/commit/d209774c6c475df4af0527580bde1e39cd496e09))

## v0.31.2 (2021-06-11)
### Fix
* Generate nested commands relative to the original function ([`d0493c9`](https://github.com/mcbeet/beet/commit/d0493c9ba17d53ebadc26260c6325ea80329ea86))

## v0.31.1 (2021-06-10)
### Fix
* Render_json doesn't pass kwargs ([#86](https://github.com/mcbeet/beet/issues/86)) ([`b85ef48`](https://github.com/mcbeet/beet/commit/b85ef48a4bbbb880d8257eb7bef0945f42d4a03c))

## v0.31.0 (2021-06-10)
### Feature
* Update latest pack format ([`80a5aad`](https://github.com/mcbeet/beet/commit/80a5aad6c37ee44a209e49af10b1eb21a04f97fa))
* Use poetry project data when available ([`aa4c823`](https://github.com/mcbeet/beet/commit/aa4c823e42914d4d9a9078315cb93b2eb16a930f))

## v0.30.0 (2021-06-10)
### Feature
* Support pyproject.toml config file ([`836573a`](https://github.com/mcbeet/beet/commit/836573a5226b524d43127eb11b5daf6d1ed57644))

## v0.29.0 (2021-06-10)
### Feature
* Add beet.contrib.format_json plugin ([`4d579be`](https://github.com/mcbeet/beet/commit/4d579bef41b20bba6ac0381b48c337e258289ea9))
* Add configurable file serializer and deserializer ([`68cf41f`](https://github.com/mcbeet/beet/commit/68cf41feb2c6b7e919016404d872b9892626a515))
* Render pack name and description with jinja ([`15bf25c`](https://github.com/mcbeet/beet/commit/15bf25caa0da57dafa63d89ae683868fde7dd88c))
* Add ctx.cache.generated ([`6b9d6b5`](https://github.com/mcbeet/beet/commit/6b9d6b52f02b55365eb1460a0722fe7dae322687))
* Make it possible to disable the cache gitignore ([`ecea21b`](https://github.com/mcbeet/beet/commit/ecea21b3f3d82b8740bd6ffdee93c4d45035acac))
* Log download and cache expiration ([`b4346c5`](https://github.com/mcbeet/beet/commit/b4346c50f68102b63468932c6becda5fc95ad873))
* Add list_files() method ([`d873e8b`](https://github.com/mcbeet/beet/commit/d873e8bb48403a8845047e8194e00f584d178e4a))

### Fix
* Update yellow shulker box loot table ([`1ead861`](https://github.com/mcbeet/beet/commit/1ead861d2eb452fbb6a087ab0b9fade3656edc99))
* Update run_beet() to use the project cache ([`3a20c69`](https://github.com/mcbeet/beet/commit/3a20c6930a9ae4a6b5cab41b4366521c89ad7198))

## v0.28.0 (2021-06-09)
### Feature
* Add beet.contrib.yellow_shulker_box plugin ([`5f7b5ec`](https://github.com/mcbeet/beet/commit/5f7b5ec9bab952edd67030dda853f709bc809a96))
* Add version substitution ([`9ed16e6`](https://github.com/mcbeet/beet/commit/9ed16e66957e8051a476ed9f3fe060e8766bda91))

## v0.27.0 (2021-06-09)
### Feature
* Support yaml config file ([`14e6dee`](https://github.com/mcbeet/beet/commit/14e6dee04aec841d2e27c22806bd35193e9bdf23))
* Support toml config file ([`2f97394`](https://github.com/mcbeet/beet/commit/2f9739447682a4834cda4c5f66be6f0dc6d70359))

### Documentation
* Typo ([`a9a1a28`](https://github.com/mcbeet/beet/commit/a9a1a28a582e651ff2217d959339bed46c372dc8))

## v0.26.0 (2021-05-26)
### Feature
* Add beet.contrib.dundervar plugin ([`2ad5024`](https://github.com/mcbeet/beet/commit/2ad50242521c1fd5459c483aead0ff013f2e853c))

### Documentation
* Remove toolchain page for the moment ([`42e01b5`](https://github.com/mcbeet/beet/commit/42e01b5a8ce7141200778fb556694ad67ae269b0))
* Add toolchain overview ([`b95fc26`](https://github.com/mcbeet/beet/commit/b95fc260fc013db2256cd66e4bae57d33e035a99))

## v0.25.0 (2021-05-20)
### Feature
* Add cache.has_changed method ([`20e3658`](https://github.com/mcbeet/beet/commit/20e365886189f96bc1b244f52da9bc89d3baddea))

## v0.24.1 (2021-05-12)
### Fix
* Use partition instead of rpartition to split namespaced id ([`336dbc1`](https://github.com/mcbeet/beet/commit/336dbc1910a665556f7798c97bacb6769692ce78))

## v0.24.0 (2021-05-12)
### Feature
* Add beet.contrib.relative_function_path plugin ([`72b5730`](https://github.com/mcbeet/beet/commit/72b57307b58082d9fc51f13451653a086249fa48))

## v0.23.0 (2021-05-09)
### Feature
* Add parse_json() to template environment ([`287acd9`](https://github.com/mcbeet/beet/commit/287acd99d2e1d2d5bc2513bf42ba93454c9e4307))

### Fix
* Change hangman nested commands destination ([`7733ec5`](https://github.com/mcbeet/beet/commit/7733ec5b9fb8e1a8ef0de2ddf2119f20f2a1cfa0))

## v0.22.5 (2021-05-07)
### Fix
* Don't reload modules from site-packages ([`de2ecab`](https://github.com/mcbeet/beet/commit/de2ecab29b22dd0cd72edb368d709868a6fe5e9e))

## v0.22.4 (2021-05-07)
### Fix
* Make hangman plugin configurable ([`cc56cd8`](https://github.com/mcbeet/beet/commit/cc56cd8116d650376aa4f052255691ae869e375a))

### Documentation
* Add file handles overview ([`f6741ac`](https://github.com/mcbeet/beet/commit/f6741ac63d3dbb12379e2df16f2c6c1bf4923b4a))

## v0.22.3 (2021-05-05)
### Fix
* Add defaults for everything ([`f229b3c`](https://github.com/mcbeet/beet/commit/f229b3c2bcba413008600fc38116ad0eede95eee))
* Tweak pack and namespace equality ([`5906fb2`](https://github.com/mcbeet/beet/commit/5906fb2e6632a845ffe6364c9785ba02ee80ea20))
* Rename pack image ([`a3007a1`](https://github.com/mcbeet/beet/commit/a3007a158875178b064aae50b384871c6f31adc7))

### Documentation
* Start writing general overview ([`fd9348d`](https://github.com/mcbeet/beet/commit/fd9348d11f7d7513ce0fd3e31864a5216880f047))

## v0.22.2 (2021-05-04)
### Fix
* Use custom PathLike ([`b569367`](https://github.com/mcbeet/beet/commit/b569367f472e4d95f1c28dc3162a49be06b602e4))

### Documentation
* Update README ([`ab8056b`](https://github.com/mcbeet/beet/commit/ab8056b8c186460a59d969faa1a81af322954421))

## v0.22.1 (2021-05-02)
### Fix
* Keep template globals across environment resets ([`02379e2`](https://github.com/mcbeet/beet/commit/02379e2f1e7b043e02b570e41ce05b1d6ab2cd87))

## v0.22.0 (2021-04-27)
### Feature
* Make it possible to temporarily disable folding ([`489ad7c`](https://github.com/mcbeet/beet/commit/489ad7c65643c14633358396389dedc7d96a4d8d))
* Add particles ([`adaaf0d`](https://github.com/mcbeet/beet/commit/adaaf0d9fbdd69bbfde42a3cf24c632b0c135d36))
* Add sounds ([`6d88263`](https://github.com/mcbeet/beet/commit/6d88263228174fa21d594398210c026d00a7130e))
* Add namespace extra ([`bd7b148`](https://github.com/mcbeet/beet/commit/bd7b1480df469fdeaf1a9ce1bf6b27051e758c24))

## v0.21.0 (2021-04-23)
### Feature
* Expose generate_path in templates ([`9354b78`](https://github.com/mcbeet/beet/commit/9354b78a3fe73d513e0b3a287d6fd0c7944d13b2))
* Add generate.function_tree() ([`f9aac53`](https://github.com/mcbeet/beet/commit/f9aac53c2d1c46076faf270bad85317a9f856911))
* Add TreeNode.root ([`0f0078f`](https://github.com/mcbeet/beet/commit/0f0078f8b182cf9df492e1281727b3d686e33865))
* Add generate.path() ([`80d2689`](https://github.com/mcbeet/beet/commit/80d26892a42fd6c7052f3041659bafbab7957b4f))
* Make it possible to specify a node key ([`2b0595e`](https://github.com/mcbeet/beet/commit/2b0595e3ee34847eceb9e6bfef725ee15eaf78d5))
* Add generate_tree ([`d37df14`](https://github.com/mcbeet/beet/commit/d37df14d6c6b45579fb64b2f7b254ac1bdd1d076))
* Output the commands in-place when the path matches the current function ([`dff5d51`](https://github.com/mcbeet/beet/commit/dff5d51a87b031557b374c669c54ca827ecf734f))
* Add beet.contrib.template_context ([`12bc6ef`](https://github.com/mcbeet/beet/commit/12bc6ef83ce62f03b6238abae351259a94c32fc0))
* Add beet.contrib.template_sandbox ([`55fbe92`](https://github.com/mcbeet/beet/commit/55fbe92c8a04d04f4696323ce4605536be3afa73))
* Ctx is no longer exposed to templates ([`00ca7e9`](https://github.com/mcbeet/beet/commit/00ca7e97513aa2638fb5cf27e48186e661b93015))
* Inject can now import services on the fly ([`edfe5af`](https://github.com/mcbeet/beet/commit/edfe5af659f4deda69c99a08ea2526d72eccc13d))
* Add prepend and append to inline_function plugin ([`e12347f`](https://github.com/mcbeet/beet/commit/e12347f1b4b96a64dc8ee5348a4d5a85b5964977))
* Add generate(render=) and make hash lowercase ([`a08c73c`](https://github.com/mcbeet/beet/commit/a08c73c8cd8bb9efc8513092cdc4c78dc07206c2))
* Render_file template source_path fallback ([`666b697`](https://github.com/mcbeet/beet/commit/666b697b5e3bb01a7093c5a589896124204833d7))
* Add generate.push() ([`40b7680`](https://github.com/mcbeet/beet/commit/40b7680465f4a0bd7888d5a9b0dba61fee8f3712))

## v0.20.1 (2021-04-22)
### Fix
* Join generate argument with current template ([`074ee28`](https://github.com/mcbeet/beet/commit/074ee288bfdf2e94af344363e511a59cd9c61572))

## v0.20.0 (2021-04-17)
### Feature
* Add generate.objective() and beet.contrib.scoreboard ([`6a5376a`](https://github.com/mcbeet/beet/commit/6a5376a237a6669283aa79885a0c21998e389b71))
* Add id and hash generate helpers ([`00cd667`](https://github.com/mcbeet/beet/commit/00cd667f94701ecffe4e31f1c8eaf1cbd923e54b))

### Fix
* Default generate.id() to {incr} ([`4429ff6`](https://github.com/mcbeet/beet/commit/4429ff6a69a3f56e94b2650897313e1aac7c6901))
* Propagate generator type and forgot return annotation for hash() ([`b1b1766`](https://github.com/mcbeet/beet/commit/b1b1766dc78bd651a8065a1d11252a2bcceb1e46))
* Don't increment registry keys unless {incr} is present ([`9786c36`](https://github.com/mcbeet/beet/commit/9786c369fa4bf3ff28d2ef5fb4dbb7263ae01f87))

## v0.19.1 (2021-04-02)
### Fix
* **generator:** Only default to content hash if hash wasn't explicitly provided ([`bee1df4`](https://github.com/mcbeet/beet/commit/bee1df4d1ea1ed12de8150c87043915f70ef5372))

## v0.19.0 (2021-03-29)
### Feature
* Make generator prefix and namespace configurable and add tests ([`4972534`](https://github.com/mcbeet/beet/commit/4972534239f1a994c3382f16973f08cecebadf0b))
* Refactor hangman plugin to support run commands syntax ([`849697b`](https://github.com/mcbeet/beet/commit/849697b4f62be42dade6e5ac6c728a156a6c583b))
* Add context generator ([`09eb6ab`](https://github.com/mcbeet/beet/commit/09eb6ab4bbaf8de0dc9ed968fc6d277a7eb0c07b))
* Add file default value ([`205c9ff`](https://github.com/mcbeet/beet/commit/205c9ff16b060ea91ab1b5eda0c1de9583ca5e6b))

## v0.18.0 (2021-03-27)
### Feature
* Add ignore_name test utility ([`e5ee8f2`](https://github.com/mcbeet/beet/commit/e5ee8f22791a8fa500a5f6093ec95ea00ef4fe51))

## v0.17.3 (2021-03-27)
### Fix
* Prevent explanation from crashing when assertrepr_compare returns None ([`0ed03ed`](https://github.com/mcbeet/beet/commit/0ed03ed8c5180455934d0bc90e294391b059e04f))

### Documentation
* Add changelog page ([`3c554ac`](https://github.com/mcbeet/beet/commit/3c554ac03be1ef71b94c52ea28ee7e404031b86a))

## v0.17.2 (2021-03-24)
### Fix
* **hangman:** Handle trailing comments ([`ff7ba22`](https://github.com/mcbeet/beet/commit/ff7ba225a099f6e5c3b5b22fb3bcfab7114acfe6))

## v0.17.1 (2021-03-24)
### Fix
* Remove dedent extension ([`ab0797a`](https://github.com/mcbeet/beet/commit/ab0797af365e9c77d6c0bf62234c232c137785bf))

## v0.17.0 (2021-03-24)
### Feature
* Add hangman plugin ([`2a96811`](https://github.com/mcbeet/beet/commit/2a96811892ad0bd4d4f858b973f10bff794eabdf))

### Documentation
* Update homepage ([`3a25a4c`](https://github.com/mcbeet/beet/commit/3a25a4cba0ca15b05b09d1e1ec8f134aefc9e0f3))
* Update ([`825181b`](https://github.com/mcbeet/beet/commit/825181bfe51abfb59d5658e38d4be67c9833d33f))
* Update cli help text ([`6093b61`](https://github.com/mcbeet/beet/commit/6093b61180031560aab4f04ba65cc75860aa9b2b))
* Add action ([`579ea4f`](https://github.com/mcbeet/beet/commit/579ea4f177f045ea3fc2d096c7d04f91de60a4ba))

## v0.16.0 (2021-03-21)
### Feature
* Support core shaders ([`69e3d19`](https://github.com/mcbeet/beet/commit/69e3d1928891891b26408ca50f6faa558df629c1))

### Fix
* Better file comparisons with source_path fast path ([`3c12aa7`](https://github.com/mcbeet/beet/commit/3c12aa7bee647d411393711e869d99f40713effe))
* Properly display edited filename on windows ([`e3c1890`](https://github.com/mcbeet/beet/commit/e3c189035d155a234aff9a9beed4caf950040e3e))

### Breaking
* ShaderProgram was renamed to Shader  ([`69e3d19`](https://github.com/mcbeet/beet/commit/69e3d1928891891b26408ca50f6faa558df629c1))

## v0.15.0 (2021-03-19)
### Feature
* Add logging ([`6505cbb`](https://github.com/mcbeet/beet/commit/6505cbb47feed1d0c4934468b67e2bd9be4aafe9))
* Add babelbox plugin ([`70e1829`](https://github.com/mcbeet/beet/commit/70e1829de45e61400c9dfcd3698ef10b41091be7))
* Add workers ([`eacd2ae`](https://github.com/mcbeet/beet/commit/eacd2ae4a6bad9fdc018f3849b748c12e9b91946))

### Fix
* Compare data for equality for json files ([`298e2e1`](https://github.com/mcbeet/beet/commit/298e2e1989d90d11dc7706c5d24e8741a86901af))

## v0.14.0 (2021-03-18)
### Feature
* Support language files and custom languages ([`abec2b1`](https://github.com/mcbeet/beet/commit/abec2b1b4f2fc27ff6b0ddf84fb9ace81834c104))

### Fix
* Only modify sys.path if the directory is not already present ([`8575d31`](https://github.com/mcbeet/beet/commit/8575d31b14c71063479af584715cfe9e7c92086f))

### Breaking
* rename pin descriptors  ([`abec2b1`](https://github.com/mcbeet/beet/commit/abec2b1b4f2fc27ff6b0ddf84fb9ace81834c104))

## v0.13.0 (2021-03-14)
### Feature
* Add plugin autoload ([`9cac58e`](https://github.com/mcbeet/beet/commit/9cac58e2ea5348509fde32ccfbd3e71a5c503678))
* Make cli extensible ([`9adb10c`](https://github.com/mcbeet/beet/commit/9adb10c5664362fb782a417eaf7b8aaf784e7e5c))

### Fix
* Don't crash when there are no entry points ([`85f6bd7`](https://github.com/mcbeet/beet/commit/85f6bd7408c98cc02b03a2a28165da2c576b42fb))

## v0.12.0 (2021-03-09)
### Feature
* Add sandstone plugin ([`cad9101`](https://github.com/mcbeet/beet/commit/cad910153131315097a6cf65f35a396ddfa525f9))

## v0.11.2 (2021-03-09)
### Fix
* Accept ProjectConfig instances for run_beet ([`9939b10`](https://github.com/mcbeet/beet/commit/9939b107c3e6dadc5e3fc8cdaba34bd06b019a53))

## v0.11.1 (2021-03-03)
### Fix
* Ignore click exceptions in error_handler ([`9544765`](https://github.com/mcbeet/beet/commit/95447651b9c40a46484d8edafc4145b587369509))

## v0.11.0 (2021-03-03)
### Feature
* Add pytest plugin for rich explanations ([`947a6b5`](https://github.com/mcbeet/beet/commit/947a6b5fe251fe630afa326e62e365d5ebaca990))
* Add whitelist ([`f5730ba`](https://github.com/mcbeet/beet/commit/f5730ba152921b64afbe4c629553c182815a7877))

## v0.10.5 (2021-02-27)
### Fix
* Overload getitem to return namespaceproxy ([`6b0b731`](https://github.com/mcbeet/beet/commit/6b0b731c77253d7cf335cda09b778feee61045d8))

## v0.10.4 (2021-02-25)
### Fix
* Change path and save ([`ecc6593`](https://github.com/mcbeet/beet/commit/ecc659385bb64fa884a01648e2f0db553542160a))

## v0.10.3 (2021-02-25)
### Fix
* Turn run_beet() into a context manager ([`852cebb`](https://github.com/mcbeet/beet/commit/852cebbb71a09be66d318cd5ce6d2f8c9d6ffb7a))

## v0.10.2 (2021-02-25)
### Fix
* Add download method ([`7951470`](https://github.com/mcbeet/beet/commit/7951470a5f7be4973816b686b311e52fd29f9a32))

## v0.10.1 (2021-02-25)
### Fix
* Use plain list to hold commands ([`9b02b77`](https://github.com/mcbeet/beet/commit/9b02b7711e3e63596f6250984a320059b6e47156))

## v0.10.0 (2021-02-24)
### Feature
* Add cache.get_path() ([`f72b51c`](https://github.com/mcbeet/beet/commit/f72b51c8aa617ff1e923fc8cad6b3f75c0566299))

### Documentation
* Add custom domain ([`899d09f`](https://github.com/mcbeet/beet/commit/899d09f0e33ab45589ffb65849abf8c8d8ae1569))
* Fix malformed table ([`3dd0a15`](https://github.com/mcbeet/beet/commit/3dd0a15ffcf9deb289e0a630d838dc0c21944251))

## v0.9.4 (2021-02-23)
### Fix
* Add 1.17 item modifiers ([`9463ac8`](https://github.com/mcbeet/beet/commit/9463ac857d36044563f712f890662720b4123608))

### Documentation
* Add toolchain ([`a6abf05`](https://github.com/mcbeet/beet/commit/a6abf0522a76e3121b6125879ae85e1c355f7e6c))

## v0.9.3 (2021-02-22)
### Fix
* Take into account pack.mcmeta in pack bool() ([`62af388`](https://github.com/mcbeet/beet/commit/62af3881a898eb4a260abeffb460df4e1d2d055e))

## v0.9.2 (2021-02-21)
### Fix
* Annotate descriptors ([`4e47cc6`](https://github.com/mcbeet/beet/commit/4e47cc6dc612eb0f804dc8f24454f5f590a24544))

## v0.9.1 (2021-02-20)
### Fix
* Make it possible to specify an existing cache and use run_beet in examples ([`5cdea1d`](https://github.com/mcbeet/beet/commit/5cdea1d46d36a4324582232a6773edefcadb4350))

## v0.9.0 (2021-02-20)
### Feature
* Add run_beet helper function ([`a2cb545`](https://github.com/mcbeet/beet/commit/a2cb5454972f768b215248fbc95575fd26a34dfc))

## v0.8.2 (2021-02-20)
### Fix
* Overload merge to automatically merge pack extras too ([`a586ee3`](https://github.com/mcbeet/beet/commit/a586ee30eb00aadb0276a6bb7b2c4b2a637ed236))

## v0.8.1 (2021-02-18)
### Fix
* Add FormattedPipelineException and use config_error_handler in subproject ([`49895e3`](https://github.com/mcbeet/beet/commit/49895e34246f39529dd984cec434863977be5da8))

## v0.8.0 (2021-02-18)
### Feature
* Remove __render__ and expose render path and render group in meta ([`adc9452`](https://github.com/mcbeet/beet/commit/adc945207098bdf4eed7699cd01a855ad899e846))
* Add ctx.override to temporarily change meta ([`c1483d0`](https://github.com/mcbeet/beet/commit/c1483d08244ed159f055d18ab487191b40a49cde))
* Expose renderer as a standalone plugin ([`e935383`](https://github.com/mcbeet/beet/commit/e935383abf7f8de9db0a7ce354b50fa78eca45fb))
* Add sandbox ([`bd538af`](https://github.com/mcbeet/beet/commit/bd538af938b740c07a1f1bdf6834816f4c476e51))
* Add explicit activate context manager ([`1e21f66`](https://github.com/mcbeet/beet/commit/1e21f66fa8068cc7309951f9924dce85ab27b333))

### Fix
* Replace exception_fallthrough with PipelineFallthroughException ([`35ace13`](https://github.com/mcbeet/beet/commit/35ace13821338f699a3426858c3b2257fbf2e73e))
* Set ctx template global in __post_init__ ([`96d928b`](https://github.com/mcbeet/beet/commit/96d928b6a81f1f272930b2ed30eac082ff455e66))
* Expose the template directories ([`7d6f7a1`](https://github.com/mcbeet/beet/commit/7d6f7a1b009770984515b09550bc36e0c7b39d96))
* Ignore cache relative to the resolved directory ([`3e77d79`](https://github.com/mcbeet/beet/commit/3e77d7929b5c2c3b71c994f52b19e2dccafbdbff))

### Documentation
* Document ctx.activate() and ctx.override() ([`286eca2`](https://github.com/mcbeet/beet/commit/286eca20b7d5b0ab64ff74048f0f8c1ecaef5e2e))

## v0.7.0 (2021-02-16)
### Feature
* Add lantern_load plugin ([`7118f10`](https://github.com/mcbeet/beet/commit/7118f10f49e574b8701004fdcc5f30dc56e89167))

## v0.6.1 (2021-02-13)
### Fix
* Make it possible to use text components and override the description in plugins ([`ad972d0`](https://github.com/mcbeet/beet/commit/ad972d011f10e7006d34c07a37f8116f7bc2227f))

## v0.6.0 (2021-02-13)
### Feature
* Add subproject helper ([`d604179`](https://github.com/mcbeet/beet/commit/d60417924b44284dac45d5ad4b23d4b5a08aee99))

### Documentation
* Add link to pipeline configuration video ([`811d426`](https://github.com/mcbeet/beet/commit/811d426ebe5943b683e957a2e98e97a8522b3122))
* Add docstring to context inject method ([`2f09ffe`](https://github.com/mcbeet/beet/commit/2f09ffe591612246c23d8997467630aa79002c75))

## v0.5.1 (2021-01-27)
### Fix
* Expose project metadata in context ([`a04081c`](https://github.com/mcbeet/beet/commit/a04081ce23c941bd240ff1187fc40645fce7e627))
* Better dotted pack name handling ([`79fccff`](https://github.com/mcbeet/beet/commit/79fccfff9d92353cebbdc631b6ae56b2e6a99be3))

## v0.5.0 (2021-01-23)
### Feature
* Add beet.contrib.minify_functions plugin ([`a7774a9`](https://github.com/mcbeet/beet/commit/a7774a9b799eac7eceb078759e02b8714da9d9c1))
* Add beet.contrib.minify_json plugin ([`78cd972`](https://github.com/mcbeet/beet/commit/78cd9728401570ad772a3684577667c126eef0a9))

### Fix
* Typo in serialization descriptor ([`edbe174`](https://github.com/mcbeet/beet/commit/edbe1740bd9bb0b85877746f693f3ba7247bbf57))

### Documentation
* Add link to plugins basics video ([`3d7a3db`](https://github.com/mcbeet/beet/commit/3d7a3dbceefeb4afc998a2599f02c441016c8c31))

## v0.4.0 (2021-01-14)
### Feature
* Handle resource pack fonts and tweak docstrings ([`57cce73`](https://github.com/mcbeet/beet/commit/57cce7380a2f9b9a15a61bac4d824e2d6ce48a2f))
* Add shaders ([`34505d9`](https://github.com/mcbeet/beet/commit/34505d99e9b6714c593a4a5f5b919d22dacd6fa2))
* Locate_minecraft() now takes into account the MINECRAFT_PATH environment variable ([`ad6668b`](https://github.com/mcbeet/beet/commit/ad6668b639a8ed6eba18cff1a41b11666b2db488))

### Fix
* Also look for the .minecraft folder in the launcher files on linux ([`5645789`](https://github.com/mcbeet/beet/commit/564578935b25193a2cbbcf8e71f44d942336a5b7))
* Strip extra underscores from normalized name ([`55b8494`](https://github.com/mcbeet/beet/commit/55b8494248098aa532fa816b0abdf6d46b236021))

## v0.3.3 (2021-01-10)
### Fix
* Tweak typing for merge implementation ([`8efa444`](https://github.com/mcbeet/beet/commit/8efa444ccf67dd25eb1fd23d4e89f07407bf404c))

### Documentation
* Add link to library overview video ([`4f37a74`](https://github.com/mcbeet/beet/commit/4f37a7496d863b0535b39a1b6c1ad3df786bc89b))

## v0.3.2 (2020-12-29)
### Fix
* Use forward slash for zipfile paths on windows ([`b605c07`](https://github.com/mcbeet/beet/commit/b605c07a06106fd97866b9c442b39313381aabb5))

### Documentation
* Link to command-line video ([`1f45b03`](https://github.com/mcbeet/beet/commit/1f45b036c55902d1736f1f63cc26202291f29842))
* Add quick start to readme ([`3310d16`](https://github.com/mcbeet/beet/commit/3310d16d5490c9554c40acb0c4d295b4d8e10e68))

## v0.3.1 (2020-12-22)
### Fix
* Default match shouldn't match anything ([`6f01d6a`](https://github.com/mcbeet/beet/commit/6f01d6a19d63d9374e575942cf40dc1b14a4df88))

## v0.3.0 (2020-12-22)
### Feature
* Add function_header plugin ([`bb73eee`](https://github.com/mcbeet/beet/commit/bb73eeef0d984ca80cfd378ab2b0a99d89a33d47))

### Fix
* Rename inline plugins ([`a6b7aaa`](https://github.com/mcbeet/beet/commit/a6b7aaa60d97bf203d771861effc0ee61425786d))

### Documentation
* Add module docstring to inline plugins ([`d829d89`](https://github.com/mcbeet/beet/commit/d829d89c815c15b34dd51ac6e3a68d563906b3c4))

## v0.2.2 (2020-12-21)
### Fix
* Trigger release to update readme ([`d409af5`](https://github.com/mcbeet/beet/commit/d409af56d4c82da5d3c2743a158128cb4ed0b062))

### Documentation
* Start writing docs ([`034c662`](https://github.com/mcbeet/beet/commit/034c662878c88d2da84c71f15d46e85c38e2e5db))
* Update readme ([`58c9822`](https://github.com/mcbeet/beet/commit/58c98226b091f3dd5994888bfdd71301dafb278f))
* Add mudkip ([`fb3cfdd`](https://github.com/mcbeet/beet/commit/fb3cfddee1b220e055659393e9ce747fddcd5a26))

## v0.2.1 (2020-12-21)
### Fix
* Include better dependencies for windows ([`b28977f`](https://github.com/mcbeet/beet/commit/b28977f206bd48b0cdae67ac1dad2e17ade81f24))

### Documentation
* Fix main branch ([`74ac998`](https://github.com/mcbeet/beet/commit/74ac998c7103ebdb9c95058e141ab1acc703670b))

## v0.2.0 (2020-12-21)
### Feature
* Trigger first automatic release ([`a5664b3`](https://github.com/mcbeet/beet/commit/a5664b3fa7f7fc6c9d1d93f1cc26f91504dd3dae))
