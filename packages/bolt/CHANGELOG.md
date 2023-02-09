# Changelog

<!--next-version-placeholder-->

## v0.30.0 (2023-02-09)
### Feature
* Macro subcommands ([`5db484e`](https://github.com/mcbeet/bolt/commit/5db484ef754bbd5eaeea0c16574ecc23e160a490))

## v0.29.0 (2023-02-06)
### Feature
* Update 1.19 ([`0a8ca58`](https://github.com/mcbeet/bolt/commit/0a8ca580f4e3b155154fd8714ddb6ccc4c13121f))

## v0.28.0 (2023-02-05)
### Feature
* Error when using unsupported statements in memo ([`e57c845`](https://github.com/mcbeet/bolt/commit/e57c845f28cd40669ace582dcb2f404cf384582d))

## v0.27.0 (2023-02-05)
### Feature
* Restore memo bindings ([`48c5fe9`](https://github.com/mcbeet/bolt/commit/48c5fe996ff5a575bf50b5bf5f572320fedfb39e))

## v0.26.0 (2023-02-02)
### Feature
* Add type annotations ([`a3970f1`](https://github.com/mcbeet/bolt/commit/a3970f1a61668c5cf772ad24eacd7a835aa1824e))

## v0.25.0 (2023-02-01)
### Feature
* Add docstrings ([`c1c1488`](https://github.com/mcbeet/bolt/commit/c1c1488d60d58abc2a66d8cd02b671831bbf4473))

## v0.24.1 (2023-02-01)
### Fix
* Update pyright ([`24120a9`](https://github.com/mcbeet/bolt/commit/24120a963b476676391a51fa25350a6a06225469))

## v0.24.0 (2023-02-01)
### Feature
* Atlas ([`8703186`](https://github.com/mcbeet/bolt/commit/87031867ab7ce7014f88ef30e129cf1b115f5945))

## v0.23.0 (2023-01-31)
### Feature
* Add memo and a bunch of tweaks ([`77326b7`](https://github.com/mcbeet/bolt/commit/77326b7056a038743a1f20511ae565cacbc15f10))

## v0.22.0 (2022-12-04)
### Feature
* Refactor identifier tracing with proper lexical scope abstraction ([`2f60bd4`](https://github.com/mcbeet/bolt/commit/2f60bd43c8affc2747c56e2d4dd4045e45561677))

## v0.21.1 (2022-12-03)
### Fix
* Default empty arguments for AstFunctionSignature ([`6c79443`](https://github.com/mcbeet/bolt/commit/6c794431fe5b4c826dea8cae54a63d8c54838ad9))

## v0.21.0 (2022-11-23)
### Feature
* Add bolt.contrib.defer ([`6a0527f`](https://github.com/mcbeet/bolt/commit/6a0527f4696081a168a5adbfbb6a5f74d4853c4b))
* Add CommandCollector ([`a07cedd`](https://github.com/mcbeet/bolt/commit/a07cedd2e4636b50494ff7cdd914050d194fe922))
* Disable mecha.contrib.inline_function_tag by default ([`a9bf8bf`](https://github.com/mcbeet/bolt/commit/a9bf8bfe3d7bb39d767c204e4f06a80cc4133d78))

## v0.20.1 (2022-10-26)
### Fix
* Reset token generator after discarding builtin identifier in interpolation ([`37f74bc`](https://github.com/mcbeet/bolt/commit/37f74bc8f9fbf60b0493bf8e158be678ced5f272))

## v0.20.0 (2022-10-24)
### Feature
* Interpolate advancement predicate ([`e4338b0`](https://github.com/mcbeet/bolt/commit/e4338b0f4004601daf9c86b169a3771f876cff16))

### Fix
* Refactor interpolation ([`44c2d0e`](https://github.com/mcbeet/bolt/commit/44c2d0ed74c8100698fa75931df626c96329b820))

## v0.19.3 (2022-10-19)
### Fix
* Reset generator to prevent dropping tokens ([`6551578`](https://github.com/mcbeet/bolt/commit/65515786d6a941a2f4e94c4e8932c0dc90faa14f))
* Update deps ([`1a00f20`](https://github.com/mcbeet/bolt/commit/1a00f208fce10a37e2ef9003d478b8dddce30d73))

## v0.19.2 (2022-10-04)
### Fix
* Reported 0 errors message ([`16e64b7`](https://github.com/mcbeet/bolt/commit/16e64b77d5516fa04687f156ace6a4ee050be95b))
* Proper error for statements used as subcommands ([`647b1c6`](https://github.com/mcbeet/bolt/commit/647b1c6685f5653bf34fdc87fab7ce2a7edc6fba))

## v0.19.1 (2022-09-12)
### Fix
* Add error for non-default args following default args ([`2af9854`](https://github.com/mcbeet/bolt/commit/2af9854d91818804b642ffe2a7b625a6412665ec))

## v0.19.0 (2022-09-11)
### Feature
* Update compilation priority depending on execution order ([`d6aa9ec`](https://github.com/mcbeet/bolt/commit/d6aa9ecf55027e411889459986d79123239ec81b))

## v0.18.1 (2022-09-11)
### Fix
* Update deps ([`89b37c1`](https://github.com/mcbeet/bolt/commit/89b37c1b1d5cac57b1fdc1f5bef0971c41dd3e1b))

## v0.18.0 (2022-09-11)
### Feature
* Positional-only, variadic, keyword-only, and variadic keyword arguments ([`6413593`](https://github.com/mcbeet/bolt/commit/64135935c8f54dbde20807cba6481202dbf394e6))

## v0.17.7 (2022-08-16)
### Fix
* Update beet ([`c494033`](https://github.com/mcbeet/bolt/commit/c494033639d389fb6a3165ddefa04d8dc3c4a08e))

## v0.17.6 (2022-08-12)
### Fix
* Import parser properly delegates to resource location parser ([#37](https://github.com/mcbeet/bolt/issues/37)) ([`a971b07`](https://github.com/mcbeet/bolt/commit/a971b07e15d7382216f90c51233e3e7762a05b47))

## v0.17.5 (2022-08-06)
### Fix
* Builtins used as dict keys are now unquoted strings ([`015ff65`](https://github.com/mcbeet/bolt/commit/015ff657229b02d5930b0a5756e95d515e8df70e))
* Only allow call expressions on builtins for interpolation ([`0526a85`](https://github.com/mcbeet/bolt/commit/0526a85af232e05255e24e07a43ee720a1bb87f4))

## v0.17.4 (2022-08-06)
### Fix
* Truncate primary expression for interpolation ([`014802f`](https://github.com/mcbeet/bolt/commit/014802fcf98314b270868503a8f4bca1a3429d31))

## v0.17.3 (2022-07-25)
### Fix
* Enable interpolation for uuid ([`39cc462`](https://github.com/mcbeet/bolt/commit/39cc4624f555874808c629000c260c2feefbb5b4))

## v0.17.2 (2022-07-25)
### Fix
* Enable interpolation for game_profile argument ([`e844f49`](https://github.com/mcbeet/bolt/commit/e844f49906fa693edf9fe509427211b2b01ad39d))

## v0.17.1 (2022-07-21)
### Fix
* Only allow imports and macros directly at scope level ([`2f069bd`](https://github.com/mcbeet/bolt/commit/2f069bd6ae7e689605303fb99fa272bdc4b17e36))

## v0.17.0 (2022-07-20)
### Feature
* Add bolt classes ([`71c1162`](https://github.com/mcbeet/bolt/commit/71c1162c99c61eb747573a370646f80b787f95f5))

## v0.16.0 (2022-07-17)
### Feature
* Make modules lazy by default ([`370a759`](https://github.com/mcbeet/bolt/commit/370a7596d0a5764dfe0c2ce5e553483f8728ab60))

## v0.15.0 (2022-07-17)
### Feature
* Add raw strings ([`e24d772`](https://github.com/mcbeet/bolt/commit/e24d7721ddd8e708735f7e3b16c50b81cbfb4a89))

## v0.14.0 (2022-07-17)
### Feature
* Ergonomic improvements for dicts without quotes ([`18c747e`](https://github.com/mcbeet/bolt/commit/18c747e74aa2500fbb47414d0bc4ea24a3af04a1))

## v0.13.0 (2022-07-17)
### Feature
* Add raise statement ([`d5654a5`](https://github.com/mcbeet/bolt/commit/d5654a58c95ea326ff01da92b88bfd2e29e48b6c))
* Add proc macro ([`97e1bea`](https://github.com/mcbeet/bolt/commit/97e1beadb033de13453ef9deee1c290bdd730f4e))

## v0.12.2 (2022-07-15)
### Fix
* Update beet ([`a4f2f97`](https://github.com/mcbeet/bolt/commit/a4f2f97feef98d9c9f624ffc82a3d8e5ff282337))

## v0.12.1 (2022-07-15)
### Fix
* Memoize command trees ([`8c8911a`](https://github.com/mcbeet/bolt/commit/8c8911ae16e3c2829c0e33dbc3a2fab248505b81))
* Make command tree updates lazy ([`ec17f74`](https://github.com/mcbeet/bolt/commit/ec17f7479072a63e8e81a8c17163d69c680a9b5e))
* Minor tweaks ([`35a537e`](https://github.com/mcbeet/bolt/commit/35a537e9a4a6e471a17cfc99b8776bdc3135fd88))

## v0.12.0 (2022-07-13)
### Feature
* Add macro imports ([`e8ca750`](https://github.com/mcbeet/bolt/commit/e8ca750c6664ffa610b09c17d00cb7f9eed445c8))

## v0.11.0 (2022-07-10)
### Feature
* Turn module manager into a mapping ([`3c486eb`](https://github.com/mcbeet/bolt/commit/3c486eb6d9ce6c9a47ec16c14342fa98db6fbfd7))
* Extract module manager from runtime ([`20e7499`](https://github.com/mcbeet/bolt/commit/20e74995ab2b44505a494e352f94d1c756ba0ec6))
* Make it possible to run the lazy plugin multiple times ([`87df070`](https://github.com/mcbeet/bolt/commit/87df070d2f528a95c06b14fb2a8b3e019e80651c))

## v0.10.0 (2022-07-09)
### Feature
* Working macro and tests ([`a0ddfba`](https://github.com/mcbeet/bolt/commit/a0ddfbab5a46b173ec8a0bd46f8e78c76a098c85))
* Start working on macro ([`e3bbb3e`](https://github.com/mcbeet/bolt/commit/e3bbb3e83dd2f60df2a4f8ca848782b7a83a2c84))

### Fix
* Update mecha ([`e6c77e9`](https://github.com/mcbeet/bolt/commit/e6c77e9d495e7de8dcc3326ea15c2edc767249f7))

## v0.9.1 (2022-07-02)
### Fix
* Allow ast node interpolation directly ([`ffa076e`](https://github.com/mcbeet/bolt/commit/ffa076efa635be32c735371e2761da954385abbf))

## v0.9.0 (2022-06-24)
### Feature
* Add bolt.contrib.lazy ([`c9f12f3`](https://github.com/mcbeet/bolt/commit/c9f12f360c70ca031acfe5f9b2f0213bc7c3fdff))
* Add compiled module execution hooks ([`0a91936`](https://github.com/mcbeet/bolt/commit/0a91936a8172ad7b2b246c38b931cac8da6a27d2))

### Fix
* Minor visual changes ([`0ab3519`](https://github.com/mcbeet/bolt/commit/0ab35197e9d8f8532c39faf4b2a03caa938077bc))

## v0.8.2 (2022-06-24)
### Fix
* Remove leftover extern plugin ([`42cc659`](https://github.com/mcbeet/bolt/commit/42cc6590bfef34cc4573ed8d2fe8404cf26c9f34))

## v0.8.1 (2022-06-18)
### Fix
* Update deps for new snapshot settings ([`6739b2b`](https://github.com/mcbeet/bolt/commit/6739b2bb0d4521de90e6162f40033d37b2550fcd))

## v0.8.0 (2022-06-18)
### Feature
* Add context managers ([`38e614e`](https://github.com/mcbeet/bolt/commit/38e614e8d38d1c62af019f2b5f08a78cff22ed0b))

## v0.7.2 (2022-06-17)
### Fix
* Only restrict builtins when sandbox is active ([`8eefb0c`](https://github.com/mcbeet/bolt/commit/8eefb0cf1f5d6f3a6b0e472ffb1da0e6b60ba5e7))

## v0.7.1 (2022-06-15)
### Fix
* Track bolt version in cached ast ([`1e5d2d1`](https://github.com/mcbeet/bolt/commit/1e5d2d119872397dadac006c18b2c3909ccf6496))

## v0.7.0 (2022-06-15)
### Feature
* Support decorators ([`3e8f60b`](https://github.com/mcbeet/bolt/commit/3e8f60bf9b7e9c74b631bdf689f4370f76f37766))

### Fix
* Change prefix of codegen variables ([`f9cc901`](https://github.com/mcbeet/bolt/commit/f9cc9013ba1dd1333a2b5a199c29c84d054e15be))

## v0.6.0 (2022-05-27)
### Feature
* Add bolt.contrib.debug_codegen ([`d504b00`](https://github.com/mcbeet/bolt/commit/d504b00867bf22770708e6eeb6190ed790f0a483))

## v0.5.1 (2022-05-27)
### Fix
* Handle uppercase python imports ([`a5e50e0`](https://github.com/mcbeet/bolt/commit/a5e50e0173b47310db43b6915d31b707b7218c3a))

## v0.5.0 (2022-05-06)
### Feature
* Iterable/mapping unpacking in json/nbt interpolation ([`32acee0`](https://github.com/mcbeet/bolt/commit/32acee0e8bbf2c831fa48c30595b63ed61f1de40))
* Unpack field for interpolation node ([`b2f6dd7`](https://github.com/mcbeet/bolt/commit/b2f6dd7017afe5c7ebc4c530f152b666c7557ba1))

### Fix
* Converter for json object ([`825f077`](https://github.com/mcbeet/bolt/commit/825f077e14bafdf719f4f488347714b5761886ac))

## v0.4.2 (2022-05-02)
### Fix
* Update mecha to fix indent bug ([`006a57a`](https://github.com/mcbeet/bolt/commit/006a57a4ff0f0e99af106e235440c5c7b06f1f71))

## v0.4.1 (2022-05-01)
### Fix
* Leftover print ([`3731f2c`](https://github.com/mcbeet/bolt/commit/3731f2c071942d0e131f42432bbd165bdf4e602e))

## v0.4.0 (2022-05-01)
### Feature
* Update beet to allow bolt files outside of the data pack ([`5c0d58c`](https://github.com/mcbeet/bolt/commit/5c0d58c181a053c2c0090d9af8b6eb96b6bc54f8))

## v0.3.4 (2022-04-30)
### Fix
* Update mecha to handle nbtlib instances properly for interpolation ([`fce1766`](https://github.com/mcbeet/bolt/commit/fce1766807e588d5a7c75b7e4e407926c0bc164d))

## v0.3.3 (2022-04-30)
### Fix
* Use next_token ([`3fb3aab`](https://github.com/mcbeet/bolt/commit/3fb3aabae017862b89d29c2124d523f2fd0c0e3a))

## v0.3.2 (2022-04-30)
### Fix
* Proper check for final expressions ([`57bb1f1`](https://github.com/mcbeet/bolt/commit/57bb1f18b09bc7b9ab04079651668341262a462b))

## v0.3.1 (2022-04-29)
### Fix
* Make message interpolation final ([`b46b165`](https://github.com/mcbeet/bolt/commit/b46b1652ee78a3224911a7a57173c9f3f236244e))

## v0.3.0 (2022-04-29)
### Feature
* Allow nbt compound interpolation ([`b6f964f`](https://github.com/mcbeet/bolt/commit/b6f964fc16805bedc1d3be94a7d042acf4112551))

## v0.2.1 (2022-04-26)
### Fix
* Use BubbleException ([`c8ce2fb`](https://github.com/mcbeet/bolt/commit/c8ce2fb478fa35aff0cf768cdb320302cf123378))

## v0.2.0 (2022-04-25)
### Feature
* Setup project ([`50b4bea`](https://github.com/mcbeet/bolt/commit/50b4beaf0faad49fad9785423378002d2bdd482a))
