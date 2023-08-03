# Changelog

<!--next-version-placeholder-->

## v0.75.0 (2023-08-03)

### Feature

* Update command tree and add macro lines ([`033302c`](https://github.com/mcbeet/mecha/commit/033302cde9760717d32cb07fdcb6961e6119dd17))

## v0.74.0 (2023-08-03)

### Feature

* Backslash continuation ([`bf1ac56`](https://github.com/mcbeet/mecha/commit/bf1ac56ef14868ef7c047474b4305e662dd17fb3))

## v0.73.1 (2023-07-20)

### Fix

* Properly stop compilation on error ([`2cc5a02`](https://github.com/mcbeet/mecha/commit/2cc5a02b8c0ec576c7e59359bd0c437be1bd474c))

## v0.73.0 (2023-06-06)

### Feature

* Mecha.contrib.nested_location ([`dbe306e`](https://github.com/mcbeet/mecha/commit/dbe306e09ba4fc8e179d5181ab64fbadf088edc9))

## v0.72.1 (2023-06-06)

### Fix

* Make dispatchers non-comparable ([`12bb3d6`](https://github.com/mcbeet/mecha/commit/12bb3d6a653192d371c17e44dea1aa0534d2c368))

## v0.72.0 (2023-05-27)
### Feature
* Add nested text resources ([`2e3a9ec`](https://github.com/mcbeet/mecha/commit/2e3a9ecffcc7e0b8bb6135a23f911acd1761d5dc))

## v0.71.2 (2023-05-08)
### Fix
* Swap mcdoc number patterns ([`ba18029`](https://github.com/mcbeet/mecha/commit/ba18029f58eedbe5b5f4461e4c053e21b9c4deec))

## v0.71.1 (2023-05-07)
### Fix
* Handle mcdoc super ([`7adfb86`](https://github.com/mcbeet/mecha/commit/7adfb8660744476b310b1e4a7ceff3eb8c76cfdc))

## v0.71.0 (2023-05-07)
### Feature
* Initial mcdoc parser ([`b732822`](https://github.com/mcbeet/mecha/commit/b73282253427399cb5358eb46c3df53f93b61266))

## v0.70.0 (2023-05-03)
### Feature
* Reusable abstract ast and dispatch ([`d4cfe86`](https://github.com/mcbeet/mecha/commit/d4cfe86a059c4c66589358c440c79d60cf2d02f3))

## v0.69.0 (2023-04-25)
### Feature
* 23w16a ([`b93bd3f`](https://github.com/mcbeet/mecha/commit/b93bd3fdcea18c5e391387fdfd9b6c2bb59d59e0))

## v0.68.0 (2023-04-25)
### Feature
* 1.19.4 ([`31570c8`](https://github.com/mcbeet/mecha/commit/31570c8aadb5f9bfdce813452a5810a36e3fde45))

## v0.67.0 (2023-02-08)
### Feature
* Update command tree ([`c74062a`](https://github.com/mcbeet/mecha/commit/c74062adb614cc1266be1d90137bfccf39f1483b))

## v0.66.0 (2023-02-06)
### Feature
* Update 1.19 ([`ab74039`](https://github.com/mcbeet/mecha/commit/ab7403976be1f0185d0b346103bd5bb6eb837d67))

## v0.65.1 (2023-02-01)
### Fix
* Update some typings ([`d08b712`](https://github.com/mcbeet/mecha/commit/d08b712ce3f8d60f52c44af6e37b154e37ee4ed7))

## v0.65.0 (2023-02-01)
### Feature
* Add output_perf ([`d2cb290`](https://github.com/mcbeet/mecha/commit/d2cb290ba819ee0c55311e248478cca6e022e0cf))

## v0.64.0 (2023-01-30)
### Feature
* Add mecha.contrib.raw ([`ec018dc`](https://github.com/mcbeet/mecha/commit/ec018dc67edf725c7c0b943260da11f9fda57986))
* Allow customizing inplace nesting ([`1ef7539`](https://github.com/mcbeet/mecha/commit/1ef75398b7447cfb2161393786382cfe734f02cb))

## v0.63.0 (2023-01-29)
### Feature
* Highest protocol version for pickle.dump to improve performance ([#232](https://github.com/mcbeet/mecha/issues/232)) ([`2045360`](https://github.com/mcbeet/mecha/commit/204536038ea5ae3d3d26f00dc5b5447f1cb5e563))

## v0.62.2 (2023-01-29)
### Fix
* Use slots for ast nodes ([`940854e`](https://github.com/mcbeet/mecha/commit/940854e4756a5001f62bc53770edd2a55f1daf90))
* Stop using importlib.resources.read_text ([`6c6b965`](https://github.com/mcbeet/mecha/commit/6c6b965a15594669641f1a595c8d16c9b1564a06))

## v0.62.1 (2023-01-29)
### Fix
* Make it possible to start compiling from a custom initial step ([`f2037ad`](https://github.com/mcbeet/mecha/commit/f2037ad8a8422cca386833db0da24bc3e6250031))

## v0.62.0 (2022-12-01)
### Feature
* Add ast node compile_hints and make it so that AstSourceMap can't end up inlined into execute ([`a6537ff`](https://github.com/mcbeet/mecha/commit/a6537ffb50df3ef7550095a8b9366d7fc47e5d52))

### Fix
* Propagate original for nested function ([`235efbd`](https://github.com/mcbeet/mecha/commit/235efbd5ebeb7a45d217ba9b46685a3086600058))

## v0.61.0 (2022-11-23)
### Feature
* Splice children ([`2e4c6a9`](https://github.com/mcbeet/mecha/commit/2e4c6a9d04112ed64dc566db03af09784ca90bac))
* Deprecate mecha.contrib.inline_function_tag ([`c748479`](https://github.com/mcbeet/mecha/commit/c748479187958bb0b4f7b1307195d3d3f9ced82d))

## v0.60.3 (2022-11-22)
### Fix
* Make SourceMapTransformer a MutatingReducer ([`c0f7109`](https://github.com/mcbeet/mecha/commit/c0f7109b2ef0bf74e21929b114146941e6d0b77c))

## v0.60.2 (2022-11-22)
### Fix
* Rename AstPhantomCommand to AstCommandSentinel ([`28cb612`](https://github.com/mcbeet/mecha/commit/28cb612fd592142dccf3ef359fe0e0c9047675d4))

## v0.60.1 (2022-11-22)
### Fix
* Default fields for phantom command ([`1d2344f`](https://github.com/mcbeet/mecha/commit/1d2344f26622f2cb5d732e3af7ad19403f2e9d43))

## v0.60.0 (2022-11-22)
### Feature
* Add mecha.contrib.source_map ([`34cf945`](https://github.com/mcbeet/mecha/commit/34cf945a089079b40761e41ae2921a51e9b48b4c))

## v0.59.2 (2022-11-15)
### Fix
* Revert looser implicit execute normalization ([`014af4f`](https://github.com/mcbeet/mecha/commit/014af4f84a8b97e9d534fa85423338cfa028d4dc))

## v0.59.1 (2022-11-14)
### Fix
* Log mecha diagnostics even when there's an error ([`6f30f0b`](https://github.com/mcbeet/mecha/commit/6f30f0b4eee25e69005b1b76fce8e672a71a92dd))

## v0.59.0 (2022-11-14)
### Feature
* Looser implicit execute normalization ([`1d0fabe`](https://github.com/mcbeet/mecha/commit/1d0fabe26ba2f97dc1f89e71fbc0c312c45957f2))

## v0.58.1 (2022-11-13)
### Fix
* Prevent inifinite recursion in CommandTree.__repr__ ([`a5a776c`](https://github.com/mcbeet/mecha/commit/a5a776c9322a97aa0e55ba8b329800c5073977c4))

## v0.58.0 (2022-11-13)
### Feature
* Add meta.nesting.generate_execute option ([`9406954`](https://github.com/mcbeet/mecha/commit/94069545a28c3aec1dbc8a950191839b95e5b6e6))

## v0.57.5 (2022-11-02)
### Fix
* Default argument parser properties ([`7e63b14`](https://github.com/mcbeet/mecha/commit/7e63b147ad1f248a84c4e8f398f5cb28295dab36))

## v0.57.4 (2022-10-19)
### Fix
* Tweak nested yaml ([`9c69a1d`](https://github.com/mcbeet/mecha/commit/9c69a1d21f581e8e9bef7e44cb41e7c6f2f18025))

## v0.57.3 (2022-10-19)
### Fix
* Update deps ([`146c8bc`](https://github.com/mcbeet/mecha/commit/146c8bcfcf8a4bf5ed5053980c878ffb061ed12b))

## v0.57.2 (2022-10-08)
### Fix
* Accurate error underline for tab freaks ([`8f1064d`](https://github.com/mcbeet/mecha/commit/8f1064d5f4d2bd9fd8dd2b357d0626de933b596e))

## v0.57.1 (2022-10-01)
### Fix
* Improve typing for AlternativeParser ([`08727c4`](https://github.com/mcbeet/mecha/commit/08727c4a8256ad8afa459eb76c02f7f7785555e4))

## v0.57.0 (2022-09-18)
### Feature
* Use context generator to implement nesting ([`c15e258`](https://github.com/mcbeet/mecha/commit/c15e25864de0f29aba4711c49b0d819e815b565d))
* Use context generator to implement nested_resources ([`4036ad5`](https://github.com/mcbeet/mecha/commit/4036ad5bd98695103f430253a2f3abffbe78a320))
* Use context generator to implement inline_function_tag ([`48dcbd7`](https://github.com/mcbeet/mecha/commit/48dcbd70633cce9a77be713fee74b468e109465f))
* Support yield in dispatcher directly and allow using yield/return for diagnostics ([`c746f5a`](https://github.com/mcbeet/mecha/commit/c746f5abe87f732e20079b2abead2fd2b821191f))

### Fix
* Update lint_basic to yield diagnostic ([`658aeda`](https://github.com/mcbeet/mecha/commit/658aeda383076431dbb72035b97ee3697e7ea5f8))

## v0.56.0 (2022-09-12)
### Feature
* Improve formatting options ([`150be65`](https://github.com/mcbeet/mecha/commit/150be6570ef7e178347d818958e31cb395de9c52))

## v0.55.1 (2022-09-11)
### Fix
* Store priority on compilation unit ([`b78c5be`](https://github.com/mcbeet/mecha/commit/b78c5bea58daeb661974a69052b2494dcc4fa986))

## v0.55.0 (2022-09-11)
### Feature
* Make it possible to adjust the priority ([`4ef97c2`](https://github.com/mcbeet/mecha/commit/4ef97c2df858049fad23e07d97bf2791b6e3b33b))

## v0.54.10 (2022-09-11)
### Fix
* Bump deps ([`ddfdf2e`](https://github.com/mcbeet/mecha/commit/ddfdf2ec4f8b77664e79ac436723dc1db910ffa6))

## v0.54.9 (2022-07-25)
### Fix
* Expose game_profile parser ([`2d0d6d6`](https://github.com/mcbeet/mecha/commit/2d0d6d6825cf8a649d5f054de7a3d419548505c9))

## v0.54.8 (2022-07-23)
### Fix
* Resolve source paths provided for validation according to the context directory ([`72e638f`](https://github.com/mcbeet/mecha/commit/72e638fe75392b70d06661c67c6405b1ac99281c))
* Add missing template_rotation and template_mirror parsers ([`718c907`](https://github.com/mcbeet/mecha/commit/718c907e263e3b516fe1881fd3f4775485d3d1e9))

## v0.54.7 (2022-07-22)
### Fix
* Properly initialize result ([`9c7ad4c`](https://github.com/mcbeet/mecha/commit/9c7ad4c9b2ae7f98a05fb19d8dfc0ad0f6982ebb))

## v0.54.6 (2022-07-20)
### Fix
* Missing fstring ([`7ad01d0`](https://github.com/mcbeet/mecha/commit/7ad01d03b901b117a8edf0bcd9a6a87c1d4f7eb6))

## v0.54.5 (2022-07-07)
### Fix
* Missing executable check ([`d646789`](https://github.com/mcbeet/mecha/commit/d6467890aa8ee42d413d3c411309a4f255eb8a89))

## v0.54.4 (2022-07-07)
### Fix
* Don't hardcode some hookable parsers ([`c18f839`](https://github.com/mcbeet/mecha/commit/c18f83979bc7ce0fbf396bcfe36fd81a5758be6d))

## v0.54.3 (2022-06-21)
### Fix
* Allow compilation step to return None to abort ([`8f3ce64`](https://github.com/mcbeet/mecha/commit/8f3ce64708607078736090370b166af215a48f5b))

## v0.54.2 (2022-06-18)
### Fix
* Update lectern for new snapshot settings ([`00ff0cf`](https://github.com/mcbeet/mecha/commit/00ff0cfe83bf9f84596c231338a9916a65d6dd4c))

## v0.54.1 (2022-06-18)
### Fix
* Make redirects conditional ([`a0046bf`](https://github.com/mcbeet/mecha/commit/a0046bf9e4dc64edd9cde51f759bcfa5123fe4fe))

## v0.54.0 (2022-06-18)
### Feature
* Use minecraft version config from beet directly ([`ed3f597`](https://github.com/mcbeet/mecha/commit/ed3f597ed62a38483c014b5e2e2a634ba2949dbf))

## v0.53.0 (2022-06-17)
### Feature
* Default to minecraft 1.19 ([`f9eda9c`](https://github.com/mcbeet/mecha/commit/f9eda9c63b9346b5b1fc17bd510cab7ab62772e8))

## v0.52.3 (2022-06-17)
### Fix
* Handle nested redirects ([`179bdcd`](https://github.com/mcbeet/mecha/commit/179bdcdbb6e62caeed100285425f0b964aa9b30d))

## v0.52.2 (2022-05-27)
### Fix
* Slice update to modify steps ([`76fb08c`](https://github.com/mcbeet/mecha/commit/76fb08c21887ce1386dae0788428b8e96cd6362a))

## v0.52.1 (2022-05-27)
### Fix
* Forgot to export DebugAstEmitter ([`3c31e46`](https://github.com/mcbeet/mecha/commit/3c31e46fa37c9ba6598abfce2e26854d5245702a))

## v0.52.0 (2022-05-27)
### Feature
* Add mecha.contrib.debug_ast ([`b61e8ab`](https://github.com/mcbeet/mecha/commit/b61e8aba97767c500c7feaf031a165ce8430dd73))
* Dump exclude ([`56673e7`](https://github.com/mcbeet/mecha/commit/56673e755c7841a10e6f4807544fa88b859b41f6))

## v0.51.0 (2022-05-22)
### Feature
* 1.19 command tree ([`1ef4324`](https://github.com/mcbeet/mecha/commit/1ef4324a542ff11464d21880bcc0dd977311d148))

## v0.50.2 (2022-05-17)
### Fix
* Allow resource redefinition if content matches ([`0e15796`](https://github.com/mcbeet/mecha/commit/0e157966e5c972811ef33e95c68ff779cd03825e))
* Allow multiline notes ([`80de947`](https://github.com/mcbeet/mecha/commit/80de94784529b1ec726b8483ab63d46a18e3679b))

## v0.50.1 (2022-05-14)
### Fix
* Allow colon in player names ([`fefb480`](https://github.com/mcbeet/mecha/commit/fefb480a60586ab5e76cc33426d4d66674a72673))

## v0.50.0 (2022-05-12)
### Feature
* Allow append/prepend for nested tag resources ([`84b0643`](https://github.com/mcbeet/mecha/commit/84b0643c0631d7d40ede44f4d86a7e74b07322f7))

## v0.49.1 (2022-05-06)
### Fix
* Take into account possible syntax extensions when checking nbt list/array homogeneity ([`de12e61`](https://github.com/mcbeet/mecha/commit/de12e617a0401182ccfebe071c6b4930988b9e7f))

## v0.49.0 (2022-05-05)
### Feature
* Make json and nbt parsers more flexible ([`2d1afa1`](https://github.com/mcbeet/mecha/commit/2d1afa173a14f35d2f13130a48959a35222dd931))

## v0.48.4 (2022-05-02)
### Fix
* Update tokenstream to fix indentation bug ([`df10dbc`](https://github.com/mcbeet/mecha/commit/df10dbcf1a31a775c8fdc961e43b2063657c5626))

## v0.48.3 (2022-05-01)
### Fix
* Auto-convert to string for resource location interpolation ([`e5e379a`](https://github.com/mcbeet/mecha/commit/e5e379aa82bd370a4d4417a21bcff9afeb796ef3))

## v0.48.2 (2022-04-30)
### Fix
* Handle nbt primitives ([`bf065f4`](https://github.com/mcbeet/mecha/commit/bf065f406776fd386ed68db8fb0ae5ad2e6535f3))

## v0.48.1 (2022-04-26)
### Fix
* Use BubbleException and WrappedException ([`31a1009`](https://github.com/mcbeet/mecha/commit/31a100981a4251466cbe4de586266646ddef8239))

## v0.48.0 (2022-04-25)
### Feature
* Remove bolt ([`10a47a9`](https://github.com/mcbeet/mecha/commit/10a47a93538fe17ee7d2a38fa18cea32a386c72c))

## v0.47.0 (2022-04-19)
### Feature
* Add bolt modules in data packs ([`1ad6291`](https://github.com/mcbeet/mecha/commit/1ad6291c3bba002c6e159f74bd57c8c0c614b70d))
* Introduce customizable source providers ([`909ed80`](https://github.com/mcbeet/mecha/commit/909ed808d36f83e26d2a34257abe159b22b40212))

## v0.46.0 (2022-04-16)
### Feature
* Make it possible to overload logical expressions ([`12c6946`](https://github.com/mcbeet/mecha/commit/12c6946bd0e7481941d50f52d4d1fa926ecac638))

## v0.45.1 (2022-04-15)
### Fix
* Better error when mutating free variable ([`09330b8`](https://github.com/mcbeet/mecha/commit/09330b872afbb99c1b14285d271c6d5b9462466d))
* Remove unnecessary isinstance check since AstJson.evaluate() always returns a json value ([`e31f1ae`](https://github.com/mcbeet/mecha/commit/e31f1aee6508b6c5958f8ea0a321a69c3ad5ab6a))

## v0.45.0 (2022-04-13)
### Feature
* Add branch overloading ([`2a7f821`](https://github.com/mcbeet/mecha/commit/2a7f821a39e1e11afdb4f509f4189fd081f5999e))
* Improve in operator overloading ([`bb706b0`](https://github.com/mcbeet/mecha/commit/bb706b08e8228dfeeb5da01a0d8a198c02f29f98))
* Add not operator overloading ([`7a6a387`](https://github.com/mcbeet/mecha/commit/7a6a38791154edbb31b40287e7ff5140bd3c1359))
* Empty lookup now means full slice ([`1567e9d`](https://github.com/mcbeet/mecha/commit/1567e9d8e298136b111569f1e5e04d5d6bd1d767))

## v0.44.0 (2022-04-13)
### Feature
* Better errors for undefined identifiers ([`7424ddf`](https://github.com/mcbeet/mecha/commit/7424ddf6748582567ab8841bf1d1f7ea97e40b45))

### Fix
* Allow `#` prefix when interpolating resource locations ([`3c1b7b5`](https://github.com/mcbeet/mecha/commit/3c1b7b510e721db6bc1c197d63232135392c6acf))
* Properly handle conditional branch scopes ([`236326b`](https://github.com/mcbeet/mecha/commit/236326b25dfe2d601d64ce1b8aa7c59960f7e5d7))

## v0.43.3 (2022-04-02)
### Fix
* Use full source path as cache key ([`f2d8944`](https://github.com/mcbeet/mecha/commit/f2d8944f8819c87b9aadfe56bc758ab1d8702e9b))

## v0.43.2 (2022-04-02)
### Fix
* Forgot to update default cache backend ([`db22e03`](https://github.com/mcbeet/mecha/commit/db22e038996db3665529ac37bef486ba0a95af54))

## v0.43.1 (2022-03-19)
### Fix
* Forgot to insert comment disambiguation for interpolation ([`4042856`](https://github.com/mcbeet/mecha/commit/4042856de1acfc6a3ab49317b211e47c418c8ffc))

## v0.43.0 (2022-03-16)
### Feature
* Add global, nonlocal, and `__rebind__()` magic method ([`9ad7921`](https://github.com/mcbeet/mecha/commit/9ad79214cf2f563b930c7683dbcd4900f4ffbb5b))
* Track target rebind ([`e4481e2`](https://github.com/mcbeet/mecha/commit/e4481e256abebe192d2d2aee7ee036fbf24479bf))

## v0.42.0 (2022-03-13)
### Feature
* Basic assignment unpacking ([`0cce327`](https://github.com/mcbeet/mecha/commit/0cce3276c8168525186e7df853e9fa10d198d9ef))
* Better coordinate interpolation ([`145a137`](https://github.com/mcbeet/mecha/commit/145a137a9028dc46933d566bf9fccf90a80ffbbf))

### Fix
* Use fallback for more interpolation types ([`272a571`](https://github.com/mcbeet/mecha/commit/272a5711c0503ecb893a4ccac342a2ad623320e7))
* Tweak coordinate regex ([`3c100fb`](https://github.com/mcbeet/mecha/commit/3c100fb43032786d3545220630dd6b9fffc8c3f2))

## v0.41.4 (2022-03-09)
### Fix
* Allow basic particle interpolation ([`ac6c10e`](https://github.com/mcbeet/mecha/commit/ac6c10ec9f0bdb83e332074e32a05f898664aea8))

## v0.41.3 (2022-03-09)
### Fix
* Strip execute run ([`d1c3206`](https://github.com/mcbeet/mecha/commit/d1c3206838bc5bfa24182d6a051f157114769d9d))
* Reject player names starting with `@` ([`82ff08e`](https://github.com/mcbeet/mecha/commit/82ff08ee91afc807eefe225731e7934ff71368cd))
* Allow objective interpolation in selector scores ([`e9646dc`](https://github.com/mcbeet/mecha/commit/e9646dcc64f1e0ea753d9ee4c0f2ad2631a4468e))
* Proper error message for nested resources behind execute ([`a27f579`](https://github.com/mcbeet/mecha/commit/a27f5796ce8d1177aca73c63487df3312c42c8a2))
* Nested resource conflicts with the particle command (close #95) ([`9938863`](https://github.com/mcbeet/mecha/commit/993886327b57af560463380787a80dfdd678f682))

## v0.41.2 (2022-03-07)
### Fix
* Proper syntax error for identifiers clashing with python keywords ([`32ad957`](https://github.com/mcbeet/mecha/commit/32ad9573f8b76c725066595fb6ab3bb9c3d1ca98))

## v0.41.1 (2022-03-07)
### Fix
* Allow single quoted strings everywhere in nested yaml ([`67ffef0`](https://github.com/mcbeet/mecha/commit/67ffef022227556ae53d84c4a0c2c1ef7f8cd9d7))

## v0.41.0 (2022-03-05)
### Feature
* Add resource location literals ([`2143802`](https://github.com/mcbeet/mecha/commit/2143802994ed94d108067d3f92019d65d794c9a4))

## v0.40.0 (2022-03-05)
### Feature
* Add mecha.contrib.nested_yaml ([`fcc75b7`](https://github.com/mcbeet/mecha/commit/fcc75b790b578c2cf2efabb350ecf96847507f8d))

### Fix
* Allow coordinates to be followed by colons ([`bcdc8de`](https://github.com/mcbeet/mecha/commit/bcdc8de679aaef1064dc9eb5bd61112d1d972f96))

## v0.39.0 (2022-03-04)
### Feature
* Add mecha.contrib.nested_resources ([`72f3387`](https://github.com/mcbeet/mecha/commit/72f33879495fc23fde7e48b1ec53dba489415190))
* Change syntax for append/prepend function ([`14a1ad9`](https://github.com/mcbeet/mecha/commit/14a1ad94a67b5850d058af247571fbd1ec5ad932))

## v0.38.2 (2022-03-01)
### Fix
* Use compatible beet dependency specifier ([`bdd6b56`](https://github.com/mcbeet/mecha/commit/bdd6b564cb4c892d361fb6c35ceacd8aae9b5102))

## v0.38.1 (2022-02-28)
### Fix
* Update beet ([`fb8d5b7`](https://github.com/mcbeet/mecha/commit/fb8d5b71c08161eea2a36a0f3a687e5fffcd931d))

## v0.38.0 (2022-02-28)
### Feature
* Update to 1.18.2 ([`b6de764`](https://github.com/mcbeet/mecha/commit/b6de764723c736ec25e766d73dacbfad66c1eb89))

## v0.37.0 (2022-02-21)
### Feature
* Introduce proper formatting option ([`af5c090`](https://github.com/mcbeet/mecha/commit/af5c09031b69d076b0629780d51a57d2459d1ef5))

## v0.36.3 (2022-02-06)
### Fix
* Support entity interpolation with player names and uuids ([`5d3a0f5`](https://github.com/mcbeet/mecha/commit/5d3a0f5be98a320a286300d59a3b7b25bd8d7147))

## v0.36.2 (2022-02-03)
### Fix
* Preserve quotes around nbt path keys with dots ([`7609f86`](https://github.com/mcbeet/mecha/commit/7609f86a4820a39cb8ba61ed7da9b98bcdaae0b1))

## v0.36.1 (2022-02-03)
### Fix
* Use explicit type to avoid weird pyright behaviour ([`f78e53d`](https://github.com/mcbeet/mecha/commit/f78e53d3fd1aaf036700e5e400914d9cc6037fc2))
* Add static overloads to `AstNbt.from_value` ([`84046dd`](https://github.com/mcbeet/mecha/commit/84046ddfba1a0997c8bf870c86e6f08cbc956a7e))
* Account for compound subscripts in nbt paths ([`1f702d6`](https://github.com/mcbeet/mecha/commit/1f702d640c74834dacc587f8618c81986e94cda1))
* Interpolate nbt paths from string values ([`1c28fed`](https://github.com/mcbeet/mecha/commit/1c28fedb2ef46fbec35553bdd43a42dacbfd36fb))

## v0.36.0 (2022-01-30)
### Feature
* Add `run function` and clean up some leftover casts ([`b0ff25b`](https://github.com/mcbeet/mecha/commit/b0ff25b5fa1aae7407a0a10066c6631fc7e8a951))

## v0.35.2 (2022-01-29)
### Fix
* Avoid shadowing diagnostics when they prevent modules from being imported ([`05711ce`](https://github.com/mcbeet/mecha/commit/05711ce451a8233dd69edacc86d727d08383f06e))
* Typo when formatting invalid coordinate exception ([`bc7a541`](https://github.com/mcbeet/mecha/commit/bc7a541b08c174fce3049c91acbfdb3e92a3ab18))
* Make it possible to check a DiagnosticCollection for errors ([`358c156`](https://github.com/mcbeet/mecha/commit/358c1562cd5913a5073095931272aaf805ed6c90))
* Make coordinate parser a bit more strict ([`b859e24`](https://github.com/mcbeet/mecha/commit/b859e246a130d469914fb1d239b8143e94a9ec1b))

## v0.35.1 (2022-01-29)
### Fix
* Allow weapon alias ([`e867989`](https://github.com/mcbeet/mecha/commit/e86798960a3788d61648010a04119e26e9c52c8a))

## v0.35.0 (2022-01-27)
### Feature
* Rename to bolt ([`ecb1944`](https://github.com/mcbeet/mecha/commit/ecb1944f90ff237101a9aa5fba85a972b3311a61))

## v0.34.4 (2022-01-27)
### Fix
* Get_module() can be called with no arguments to retrieve the executing module ([`f77cf62`](https://github.com/mcbeet/mecha/commit/f77cf62148bbdd712409591975b96978fff15701))

## v0.34.3 (2022-01-26)
### Fix
* Properly track import stack ([`c0de873`](https://github.com/mcbeet/mecha/commit/c0de873d61642d582d0b2e16a98f12c12bc7bd99))

## v0.34.2 (2022-01-26)
### Fix
* Proper import error when the module doesn't exist ([`f1ae4c8`](https://github.com/mcbeet/mecha/commit/f1ae4c8306f9bc9d9547e19af627714accb068bc))
* Don't use modified ast to import modules ([`96ee329`](https://github.com/mcbeet/mecha/commit/96ee329b1570027853b3544880407b3720ba3fca))

## v0.34.1 (2022-01-22)
### Fix
* Patch schedule clear argument ([`b648e98`](https://github.com/mcbeet/mecha/commit/b648e98b63aa17f036d13ce34c6feb8ca45c606a))

## v0.34.0 (2022-01-14)
### Feature
* Add loop_info ([`5173835`](https://github.com/mcbeet/mecha/commit/5173835e0667fc0a0a154abd65a401c1beff7eed))

## v0.33.1 (2022-01-14)
### Fix
* Allow specifying tree root using keyword argument ([`4d1e85c`](https://github.com/mcbeet/mecha/commit/4d1e85cd7b0c3b229a82b29ec1979d626b1b2604))

## v0.33.0 (2022-01-14)
### Feature
* Add del statements ([`7679582`](https://github.com/mcbeet/mecha/commit/76795820a4e81f5797e6d8dfe757858b25bd46f7))

## v0.32.1 (2022-01-14)
### Fix
* Properly report empty blocks ([`4fca8a5`](https://github.com/mcbeet/mecha/commit/4fca8a51504f609a371f12be9ba33471fb44799c))

## v0.32.0 (2022-01-14)
### Feature
* Add slicing ([`e6757fd`](https://github.com/mcbeet/mecha/commit/e6757fd8d73554544bf5343831aa9c4da9f4f6e0))

## v0.31.4 (2022-01-14)
### Fix
* Make ast options into sets and properly handle item_slot ([`9231bc3`](https://github.com/mcbeet/mecha/commit/9231bc3fb964cb3f5e564fad7ba3014e27a4c0e0))
* Sort ast options ([`56bd955`](https://github.com/mcbeet/mecha/commit/56bd955d602d65caae3af907b45c58843bd6a7cb))

## v0.31.3 (2022-01-14)
### Fix
* Proper scoreboard_slot handling ([`4740d78`](https://github.com/mcbeet/mecha/commit/4740d780ebd3662a71e39e995e0c50eb77e90dad))

## v0.31.2 (2022-01-13)
### Fix
* No scientific notation when serializing numbers ([`e923224`](https://github.com/mcbeet/mecha/commit/e923224acc1c308e59dbdc44e2822f4db912a075))

## v0.31.1 (2022-01-12)
### Fix
* Make it possible to spread nbt paths on multiple lines ([`8c66564`](https://github.com/mcbeet/mecha/commit/8c66564a6190aaf40c84b0cfce438ce128bc76d4))

## v0.31.0 (2022-01-10)
### Feature
* Support item and attribute assignment ([`459a2da`](https://github.com/mcbeet/mecha/commit/459a2da008e5886dcf1a82d61b21e31a381ae7bc))
* Support list and dict unpacking ([`a0267a4`](https://github.com/mcbeet/mecha/commit/a0267a47e3088ed23b93d964f0f51a46fd980ec5))
* Support keywords and unpacking for function calls ([`fbd5c9b`](https://github.com/mcbeet/mecha/commit/fbd5c9b40075513355a99869339a750d0b83c69f))
* Interpolate coordinates ([`6f8f009`](https://github.com/mcbeet/mecha/commit/6f8f009e5f6dfa92fb99a326090391b533290cde))

## v0.30.0 (2022-01-09)
### Feature
* Remove providers, add global ctx again, and tweak generate_tree ([`e03969e`](https://github.com/mcbeet/mecha/commit/e03969efe4d177f7e2ae2b67e4e78f047478ef01))

## v0.29.0 (2021-12-25)
### Feature
* Add scripting sandbox ([`ae343d2`](https://github.com/mcbeet/mecha/commit/ae343d262525880dd63ff4305183d201646cc88a))
* Expose generate utilities ([`9ef34c6`](https://github.com/mcbeet/mecha/commit/9ef34c6e53f01ba6e1d58bfcdc2d54eea3a12d85))

### Fix
* Store builtin names on the runtime ([`bc747e0`](https://github.com/mcbeet/mecha/commit/bc747e0cf17d20897c5fb6769750185b5024f6e1))

## v0.28.1 (2021-12-24)
### Fix
* Off-by-one line mapping ([`7fcd2da`](https://github.com/mcbeet/mecha/commit/7fcd2dab6b602fd000f7efc5a28a63089145c00c))
* Import regular python modules through helper ([`6ff1de3`](https://github.com/mcbeet/mecha/commit/6ff1de302c09dba220ae450c7904d8a8f4a5a1ce))

## v0.28.0 (2021-12-23)
### Feature
* Provide ctx and current_path through runtime import ([`c62167a`](https://github.com/mcbeet/mecha/commit/c62167aa7f9fa543ea6eeaa5646adf3125bcc923))

### Fix
* Allow optional separator for imported names ([`e07af65`](https://github.com/mcbeet/mecha/commit/e07af658fd9efdda919ec6c2de412a73fd9be823))

## v0.27.2 (2021-12-23)
### Fix
* Proper execution order for interpolation with nested root ([`2bab7b2`](https://github.com/mcbeet/mecha/commit/2bab7b2d1ba06924b2770dc6dd4fed664a10972a))
* Report unserializable nodes and remove MessageReferenceSerializer ([`137022d`](https://github.com/mcbeet/mecha/commit/137022dff37fef73a8e7ce8cdc90876264e14d23))

## v0.27.1 (2021-12-20)
### Fix
* Invalid interpolation for keys in selector arguments and block states ([`3e8999f`](https://github.com/mcbeet/mecha/commit/3e8999f67651dd67e67c59ffd9a166b0373288ef))

## v0.27.0 (2021-12-19)
### Feature
* Add mecha.contrib.inline_function_tag ([`7c5f37a`](https://github.com/mcbeet/mecha/commit/7c5f37a5dffbaa4769d29ff8592a73193a69d8a1))

### Fix
* Refactor statistics json output ([`cd90092`](https://github.com/mcbeet/mecha/commit/cd900922efcf9bf58c5e14d39d9c7412358826f6))

## v0.26.0 (2021-12-19)
### Feature
* Add append and prepend to nested functions ([`389ed4f`](https://github.com/mcbeet/mecha/commit/389ed4fcd290090e88daedb6af65773d7986528e))

### Fix
* Add pass statement ([`f47a177`](https://github.com/mcbeet/mecha/commit/f47a17773e1172ea7b090a493db6054e858e9ee3))

## v0.25.2 (2021-12-18)
### Fix
* Update README ([`3acfe60`](https://github.com/mcbeet/mecha/commit/3acfe601b10614b2ab16dd96f8193e38a9eee1e5))

## v0.25.1 (2021-12-18)
### Fix
* Sort entity types properly ([`f3847c4`](https://github.com/mcbeet/mecha/commit/f3847c486c5ebe8b7296b0e194fce9359ee9cb50))

## v0.25.0 (2021-12-18)
### Feature
* Add --json option to output stats in json file ([`a74bcf5`](https://github.com/mcbeet/mecha/commit/a74bcf594e30504ab887a46af4a0acf0d9737aa1))

## v0.24.4 (2021-12-18)
### Fix
* Break out of infinite loop when there's no execute subcommand ([`d432d8c`](https://github.com/mcbeet/mecha/commit/d432d8c5995b51d76f676c09df2f8167bc40a400))

## v0.24.3 (2021-12-18)
### Fix
* Disable ast cache for cli ([`4d44c24`](https://github.com/mcbeet/mecha/commit/4d44c24eebe71654b627ef884ca50d11d4092ae3))

## v0.24.2 (2021-12-18)
### Fix
* Update README ([`2deaeb9`](https://github.com/mcbeet/mecha/commit/2deaeb962cbc8d6a96f48bed4e474b05ed0d1a48))

## v0.24.1 (2021-12-18)
### Fix
* Move resources in one place ([`d3fdfa7`](https://github.com/mcbeet/mecha/commit/d3fdfa7ea14d94a1ae00e86bcb08d58403f80396))

## v0.24.0 (2021-12-18)
### Feature
* Add mecha.contrib.statistics and --stats option ([`eaf28a1`](https://github.com/mcbeet/mecha/commit/eaf28a1963de9b0c9331b00aaab8aad45b20dea8))

## v0.23.0 (2021-12-16)
### Feature
* Add nesting for schedule command ([`eeb15f6`](https://github.com/mcbeet/mecha/commit/eeb15f6c007f69e8323fabfc768bc30e80d8150c))

### Fix
* Only call nestde functions behind execute ([`0096cce`](https://github.com/mcbeet/mecha/commit/0096cce671b34cfa5a4774d4ae9e4ce2d92f2dff))

## v0.22.1 (2021-12-16)
### Fix
* Default to 1.18 ([`4362542`](https://github.com/mcbeet/mecha/commit/4362542f116c9cdab318d248293743025e08027e))

## v0.22.0 (2021-12-16)
### Feature
* Add python colon ([`14fa47b`](https://github.com/mcbeet/mecha/commit/14fa47b9a7a3f2f6eaa88b6927116292f0480b8d))

## v0.21.0 (2021-12-14)
### Feature
* Lower elif statements ([`c49122f`](https://github.com/mcbeet/mecha/commit/c49122fe4aa37f042d81c66e6572b3206efe62c5))

### Fix
* Edge-case for optional resource locations ([`a55b3d6`](https://github.com/mcbeet/mecha/commit/a55b3d60a4331eabb92fe1b2f5e6da8d51f08251))

## v0.20.3 (2021-12-07)
### Fix
* Handle block_marker particles ([`25bc124`](https://github.com/mcbeet/mecha/commit/25bc124ae6c9ab76ecea3204b512327e1d999bd5))
* Shallow codegen snapshots ([`28d8696`](https://github.com/mcbeet/mecha/commit/28d8696f4946ac3da7dcf64f5644287e5057970a))
* Use specialized nodes for literals ([`676fc54`](https://github.com/mcbeet/mecha/commit/676fc54ce3328917e50451f30ea85271e803c865))

## v0.20.2 (2021-12-06)
### Fix
* Small optimization and update tokenstream to get sorted explanations ([`510da71`](https://github.com/mcbeet/mecha/commit/510da716aec9b393733bcb13e186e2c93da23317))

## v0.20.1 (2021-12-06)
### Fix
* Make line mapping more compact ([`4044ce4`](https://github.com/mcbeet/mecha/commit/4044ce4355946f334c14e7b891aa4faf3a77bea1))

## v0.20.0 (2021-12-05)
### Feature
* Add import statements ([`970bd01`](https://github.com/mcbeet/mecha/commit/970bd017d8104ea2c54ebc85c2d2c58ffe735e9f))
* Inject context object ([`98e6727`](https://github.com/mcbeet/mecha/commit/98e672712819d37f34856a1fa5701157dc0cfbbe))
* Expose ctx ([`e1714f0`](https://github.com/mcbeet/mecha/commit/e1714f0bdb1fc473e3fecfe28818294bf4692501))
* Add yield statements ([`410e60a`](https://github.com/mcbeet/mecha/commit/410e60a35266ed5e66ca52a3c4aaa30064d26627))
* Add globals ([`7d934a2`](https://github.com/mcbeet/mecha/commit/7d934a20f82cad8b97f8126a03cee0a5e086227e))
* Tweak constraints and make it possible to convert tuples to ranges ([`f130359`](https://github.com/mcbeet/mecha/commit/f130359b5b3768b7dc9d59a46a24d9e808a30497))
* Add f-strings ([`88b12d2`](https://github.com/mcbeet/mecha/commit/88b12d2cf64296d8cb228d3817d9db8d93f727e2))
* Add tuples ([`80534e5`](https://github.com/mcbeet/mecha/commit/80534e5af70d2459aef4215b46912ecf5316e716))

## v0.19.0 (2021-12-05)
### Feature
* Track line numbers and rewrite tracebacks coming from generated code ([`8582212`](https://github.com/mcbeet/mecha/commit/8582212361aed3fa0c6f6dc575cf9d18725478d1))

### Fix
* Add exception handling to dispatcher ([`d8e9e95`](https://github.com/mcbeet/mecha/commit/d8e9e9563a6d4576efa815e0e4fb3d8f96eea04e))
* Typo when tracking attribute source location ([`500441d`](https://github.com/mcbeet/mecha/commit/500441d959ba670ef70936a659089160e7584090))

## v0.18.0 (2021-12-04)
### Feature
* Interpolation now works on most nodes instead of command arguments specifically ([`288f836`](https://github.com/mcbeet/mecha/commit/288f836fff0c447bb743d89b46b1dfc06d53b7f8))
* Add codegen ([`0d4409f`](https://github.com/mcbeet/mecha/commit/0d4409ffa271f8968f16a84a4be20063e920c0de))

### Fix
* Invalidate ast cache on version bumps ([`0cd634c`](https://github.com/mcbeet/mecha/commit/0cd634c5deffe0bbbe1efa4f1498364b28a6f266))
* Forgot to take into account number of matched fields when sorting rules ([`d13fa3c`](https://github.com/mcbeet/mecha/commit/d13fa3c06a42d6cfe28b8e775ba3af4e77093cff))
* Convert normalizers to parsers and get rid of normalize step ([`2c44606`](https://github.com/mcbeet/mecha/commit/2c44606e146d1d27a6061cf056fb931a08a51147))

## v0.17.0 (2021-12-01)
### Feature
* Parse lists and dicts ([`5b1776b`](https://github.com/mcbeet/mecha/commit/5b1776be44c63392060e56f47a03082dcf201871))

## v0.16.0 (2021-12-01)
### Feature
* Parse interpolated arguments ([`1e364ff`](https://github.com/mcbeet/mecha/commit/1e364ffa65e757378a42fc82ec3774eb0275e7ff))
* Parse functions ([`717b450`](https://github.com/mcbeet/mecha/commit/717b45041091c3462105525d488ded48318cfd8b))
* Make it possible to swap the cache backend ([`2870424`](https://github.com/mcbeet/mecha/commit/2870424013d1f046b99bf101d9f006b99a6e103b))
* Parse primary expressions ([`1c9033c`](https://github.com/mcbeet/mecha/commit/1c9033c119e20986209fa17730db68ff580345af))

### Fix
* Redefine comments and literals in ResetSyntaxParser ([`3b7ed25`](https://github.com/mcbeet/mecha/commit/3b7ed25ca309c1410a8846ece0bb4229099ca078))
* Add custom repr for AstChildren ([`1371be9`](https://github.com/mcbeet/mecha/commit/1371be9b73f6e8849a7b3752b3f5417ced6618f3))

## v0.15.1 (2021-11-27)
### Fix
* Iterate over indices instead of arguments values ([`0f6d0ae`](https://github.com/mcbeet/mecha/commit/0f6d0aebfb659f3a8d9e3ce01ba48d72ff5ea833))

## v0.15.0 (2021-11-27)
### Feature
* Parse assignment target, for loop, break, continue ([`ef25788`](https://github.com/mcbeet/mecha/commit/ef25788227576bcf35b7b8cc369653d6609efae3))

### Fix
* Allow json-flavored keywords ([`fff9f13`](https://github.com/mcbeet/mecha/commit/fff9f13dafad6ec85bd335e59c15be7dee450ebe))

## v0.14.0 (2021-11-26)
### Feature
* Start working on scripting ([`d9ba6d3`](https://github.com/mcbeet/mecha/commit/d9ba6d3b4d18bc5e5cbe6a76391646c6f0736758))
* Export annotate_diagnostics utility ([`8ac1026`](https://github.com/mcbeet/mecha/commit/8ac1026ec7b6dde5f49057e20cfd7c2cdd4ef8cb))
* Add standalone ResetSyntaxParser ([`602a975`](https://github.com/mcbeet/mecha/commit/602a9758e35ee702d6fa7aaa44ee13fa1f3faaed))

### Fix
* Continuations are no longer allowed for nested execute ([`59a8e74`](https://github.com/mcbeet/mecha/commit/59a8e74c3416c58327827820bd99c39417cb13ad))
* Don't keep using the same rules when the node changes in mutating reducer ([`89d92f6`](https://github.com/mcbeet/mecha/commit/89d92f6e50e802873dda7a5960819b95fa74ef5f))
* Use start() instead of pos when reporting invalid escape sequence position ([`e9cc97b`](https://github.com/mcbeet/mecha/commit/e9cc97bd90b551e6163d83316c423daa7aec3cfc))
* Forgot to explicitly export ImplicitExecuteNormalizer ([`4c5298a`](https://github.com/mcbeet/mecha/commit/4c5298afcb1a4a50b5a3674be38d637e503fc4f8))

## v0.13.3 (2021-11-20)
### Fix
* Don't use resource_location for parsing objective criteria ([`d8b72e1`](https://github.com/mcbeet/mecha/commit/d8b72e1392f6df64f42d7615c124b40197307eda))

## v0.13.2 (2021-11-20)
### Fix
* Update README ([`3557cb6`](https://github.com/mcbeet/mecha/commit/3557cb670d2c5e87441e03c12ba1d495603f5b8d))

## v0.13.1 (2021-11-20)
### Fix
* Add info about the command-line entrypoint on the README ([`750ec5e`](https://github.com/mcbeet/mecha/commit/750ec5e8b340a6fe6c75122ea664a373351bdfd3))

## v0.13.0 (2021-11-20)
### Feature
* Add cli entrypoint ([`6f291f3`](https://github.com/mcbeet/mecha/commit/6f291f301149e8ab72feb91671209106b022cb54))

### Fix
* Better error message when the minecraft version is invalid ([`bd35f9d`](https://github.com/mcbeet/mecha/commit/bd35f9d9e41b9782d90966cb6953a5ba145b007c))

## v0.12.4 (2021-11-19)
### Fix
* Improve keep comments behavior for commands with unknown locations ([`bdaccbb`](https://github.com/mcbeet/mecha/commit/bdaccbbeab53b91eb92aa0c6ea70db9511b7092c))
* Handle execute expand in mecha.contrib.nesting ([`6d57f56`](https://github.com/mcbeet/mecha/commit/6d57f560b2edf779c2dada47ca696dc3c8be2a8a))

## v0.12.3 (2021-11-19)
### Fix
* Refactor multiline argument handling and make block and item parsers more modular ([`0badf8c`](https://github.com/mcbeet/mecha/commit/0badf8ccc75176c19128dc4922e80347fc0924c6))

## v0.12.2 (2021-11-18)
### Fix
* Quick fix for messages spanning over multiple lines accidentally ([`d065c8b`](https://github.com/mcbeet/mecha/commit/d065c8b42bf6ac22ae76735d3095eff7ec76b6a9))

## v0.12.1 (2021-11-18)
### Fix
* Remove error message and automatically activate multiline when using nesting ([`8594bf0`](https://github.com/mcbeet/mecha/commit/8594bf02a306a6622c25d3fd584c299b0d08fe17))

## v0.12.0 (2021-11-18)
### Feature
* Add mecha.contrib.nesting ([`94594da`](https://github.com/mcbeet/mecha/commit/94594da2f5602ff6048768464137c8da89e00e27))
* Add cli command for dumping mecha ast ([`f0cb044`](https://github.com/mcbeet/mecha/commit/f0cb044a40594225aea49a566387b6f0d67b8391))

### Fix
* Keep track of the current step in the database ([`c5a7737`](https://github.com/mcbeet/mecha/commit/c5a77374d4439e362cd480a1fe29e3bfb18f8ef3))
* Make it possible to create resource location nodes from strings ([`6644606`](https://github.com/mcbeet/mecha/commit/6644606269e4b4674e363bbb3bc3c108c6642fbf))

## v0.11.1 (2021-11-16)
### Fix
* Handle possible conflicts between execute shorthands and commands ([`c10f8cb`](https://github.com/mcbeet/mecha/commit/c10f8cbed99a7a4357d3d7f7b184d19e366a89eb))

## v0.11.0 (2021-11-16)
### Feature
* Add keep_comments option ([`efda05a`](https://github.com/mcbeet/mecha/commit/efda05a72e361429cad309fedce477580212bb90))

## v0.10.0 (2021-11-16)
### Feature
* Add mecha.contrib.implicit_execute ([`835660f`](https://github.com/mcbeet/mecha/commit/835660f92fcfa9473211c84b2ed754096afb23a8))

## v0.9.2 (2021-11-16)
### Fix
* Tweak styling for diagnostic annotations ([`f4e3fde`](https://github.com/mcbeet/mecha/commit/f4e3fdeeb34d3564d39698336e8d66cc321d8fd3))

## v0.9.1 (2021-11-16)
### Fix
* Forgot final newline in mecha.contrib.annotate_diagnostics ([`b665a94`](https://github.com/mcbeet/mecha/commit/b665a948c80cb4296721a6b7d55011106c057e9c))

## v0.9.0 (2021-11-16)
### Feature
* Add mecha.contrib.annotate_diagnostics ([`2084667`](https://github.com/mcbeet/mecha/commit/208466709f0b2e1fc1c7a48738152d761681fb55))
* Add readonly option and setup examples ([`bdb7b1d`](https://github.com/mcbeet/mecha/commit/bdb7b1db66907e1d5eb85a6653e02f9dfd0bdea7))

### Fix
* Report diagnostics with logger.warning instead of logger.warn ([`155d01c`](https://github.com/mcbeet/mecha/commit/155d01cd5215894d16a49137d92c4da8c2482696))
* Add SingleLineConstraint ([`f649b4a`](https://github.com/mcbeet/mecha/commit/f649b4a7bc1cf74725724c22c1fb5ad7767ce03b))

## v0.8.2 (2021-11-08)
### Fix
* Prevent error when the location is outside the view ([`96c8005`](https://github.com/mcbeet/mecha/commit/96c800527a6b02ba14a47be74976979c9e534294))

## v0.8.1 (2021-11-08)
### Fix
* Database.current is now properly updated ([`e74cd13`](https://github.com/mcbeet/mecha/commit/e74cd13b013df43911a463c5a0c7a457e193f672))

## v0.8.0 (2021-11-07)
### Feature
* Add mecha.contrib.relative_location ([`7270458`](https://github.com/mcbeet/mecha/commit/72704581a8c088c8852e5c30f5ec111ccf6c4c05))

## v0.7.2 (2021-11-06)
### Fix
* Prevent minor caching inconsistency ([`5457144`](https://github.com/mcbeet/mecha/commit/5457144bf210cb71a61c9f601bd75ac51e268797))

## v0.7.1 (2021-11-05)
### Fix
* Typo when using set_location ([`2d16d63`](https://github.com/mcbeet/mecha/commit/2d16d6327ce63e67214843fe84b277c6118f0aa5))

## v0.7.0 (2021-11-05)
### Feature
* Add mecha.contrib.messages ([`99b62de`](https://github.com/mcbeet/mecha/commit/99b62de825a17552489d7b379c79be8b6adf0f34))
* Default diagnostic location to the location of the node ([`b3b7cca`](https://github.com/mcbeet/mecha/commit/b3b7cca1d90fc44fb2a23f335120d65cbd144e5d))
* Add AstJson.from_value ([`5ddfdf0`](https://github.com/mcbeet/mecha/commit/5ddfdf0eddca5851529ca24e5c3f5c35a9be2124))

## v0.6.2 (2021-10-23)
### Fix
* Add discord badge ([`d721c44`](https://github.com/mcbeet/mecha/commit/d721c4425119864c93d0d5a17e0b244ef6c18ba3))

## v0.6.1 (2021-10-20)
### Fix
* Move InvalidEscapeSequence and UnrecognizedParser ([`f17030c`](https://github.com/mcbeet/mecha/commit/f17030c9db2424d4e7a90df88c24b624d938d8df))

## v0.6.0 (2021-10-20)
### Feature
* Make it possible to emit new files during compilation ([`a8bff86`](https://github.com/mcbeet/mecha/commit/a8bff869f493a5080c291d59d21f1d9811bbd22d))
* Show formatted code when logging diagnostics ([`19e3974`](https://github.com/mcbeet/mecha/commit/19e3974ac4d4c8db8ba5a6bc858fa10fd158813b))

### Fix
* Sort diagnostics ([`0887b77`](https://github.com/mcbeet/mecha/commit/0887b7736a6c232f867ae72bbad6562697764c4d))

## v0.5.11 (2021-10-18)
### Fix
* Provide "annotate" through extra logging argument ([`e88ad04`](https://github.com/mcbeet/mecha/commit/e88ad0437f0623cc77fee6cfff12c1451fd41dcc))

## v0.5.10 (2021-10-17)
### Fix
* Handle tag and team selector argument without value ([`1ba966c`](https://github.com/mcbeet/mecha/commit/1ba966c62cb9e8077785a888ede64f6b4986b175))
* Handle fake player names with all kinds of special characters ([`286bfd8`](https://github.com/mcbeet/mecha/commit/286bfd8fe8729ebc3bd453dd5da8214856d200ac))
* Player names can be up to 40 characters not 16 ([`80ba827`](https://github.com/mcbeet/mecha/commit/80ba8275ed6d97845765fc6f3c9a2efad923509a))
* Handle json unicode escaping and other json tweaks ([`4935221`](https://github.com/mcbeet/mecha/commit/49352212fe008c7b5bffbdd94a5fa437d35a737b))

## v0.5.9 (2021-10-13)
### Fix
* Properly check range boundaries when serializing ([`5230024`](https://github.com/mcbeet/mecha/commit/52300241ed11ac0671cf258d7f5438164cf6f678))

## v0.5.8 (2021-10-10)
### Fix
* Make it possible to omit functions from compilation with match option ([`aabddf6`](https://github.com/mcbeet/mecha/commit/aabddf6200e1fd6449f96f916316afadbc37a795))

## v0.5.7 (2021-10-09)
### Fix
* Add logging for ast cache ([`c1bd76b`](https://github.com/mcbeet/mecha/commit/c1bd76beaa3262ec9b17d95267a050aa7aa16b1f))

## v0.5.6 (2021-10-09)
### Fix
* Fast path to avoid traversing ast when there are no rules ([`72322af`](https://github.com/mcbeet/mecha/commit/72322af610b725ec28cd6322cb8a5220beb1b7ae))
* Add ast cache ([`7ae025a`](https://github.com/mcbeet/mecha/commit/7ae025a635196d9abc0780ab5b8a3d8923a64c35))

## v0.5.5 (2021-10-09)
### Fix
* Handle more version formats in config ([`117bda1`](https://github.com/mcbeet/mecha/commit/117bda1f3a9c0617e7279f59777a7808c37e7fd4))

## v0.5.4 (2021-10-09)
### Fix
* Remove unnecessary args in serializer ([`cf041d6`](https://github.com/mcbeet/mecha/commit/cf041d6412cb63e79f8af5d89ec05c22f077576b))
* Add 1.18 command tree and handle player names and objectives with no length restriction ([`f1ffaa5`](https://github.com/mcbeet/mecha/commit/f1ffaa576d216d039d779179c22f5b5ce0f46678))

## v0.5.3 (2021-10-09)
### Fix
* Handle shortened UUID ([`8c2659b`](https://github.com/mcbeet/mecha/commit/8c2659b53f510b37f2fcb6274c87cf22c2e80af1))

## v0.5.2 (2021-10-09)
### Fix
* Don't log messages directly to avoid wrong percent formatting ([`abe1f99`](https://github.com/mcbeet/mecha/commit/abe1f99f8fc0765c10dcdee8d35bba29cdfac39d))
* Handle percent sign in player names ([`276cac5`](https://github.com/mcbeet/mecha/commit/276cac5131542e018a0b19dcd44cbe5b5c15f9fc))

## v0.5.1 (2021-10-09)
### Fix
* Update tokenstream to handle windows line endings ([`6d780dd`](https://github.com/mcbeet/mecha/commit/6d780dd11deb98b3fd9d44124439a051eba6275c))

## v0.5.0 (2021-09-29)
### Feature
* Add compilation database and refactor compile method ([`18d7b7f`](https://github.com/mcbeet/mecha/commit/18d7b7f2fc747e73bbb877b2a558abac1939ea0b))

## v0.4.0 (2021-09-26)
### Feature
* Add diagnostics, beet plugin, and basic linter ([`93fe177`](https://github.com/mcbeet/mecha/commit/93fe177cccc5635876ab388740380f17a42beecf))

### Fix
* Make it possible to configure the version ([`67ff495`](https://github.com/mcbeet/mecha/commit/67ff49560e72f4a8d04626c7a9ffca67cf676188))

## v0.3.6 (2021-09-21)
### Fix
* Proper rule baking ([`38e03fb`](https://github.com/mcbeet/mecha/commit/38e03fbd963237293671b2f5d0d47aed4ef1cf48))
* Also disambiguate when not in multiline mode ([`ee8e747`](https://github.com/mcbeet/mecha/commit/ee8e747ccd1c0724607b180259635c1b9c639453))

## v0.3.5 (2021-09-21)
### Fix
* Allow # and $ at the beginning of fake player names ([`4b7fc56`](https://github.com/mcbeet/mecha/commit/4b7fc56b5e6d7462aee2acda5de9754d0b821f47))

## v0.3.4 (2021-09-21)
### Fix
* Make it possible to provide a dict to add_commands ([`29b94f5`](https://github.com/mcbeet/mecha/commit/29b94f5712da74c0d346553c237a513ebe0910c2))

## v0.3.3 (2021-09-21)
### Fix
* Allow specifying version with dots ([`e4c9ba6`](https://github.com/mcbeet/mecha/commit/e4c9ba6256bc3ad803984a6a7bc68844b57c391a))

## v0.3.2 (2021-09-21)
### Fix
* Separate reducer and mutating reducer ([`730792c`](https://github.com/mcbeet/mecha/commit/730792c3297ad5e574ea5ff75a8463563f51b770))

## v0.3.1 (2021-09-21)
### Fix
* Remember current line indentation for the following terms ([`9691684`](https://github.com/mcbeet/mecha/commit/9691684532a30aba2b71fb3b4ec824c26889de96))

## v0.3.0 (2021-09-19)