# Changelog

<!--next-version-placeholder-->

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
