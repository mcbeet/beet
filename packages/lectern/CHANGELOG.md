# Changelog

<!--next-version-placeholder-->

## v0.10.1 (2021-04-25)
### Fix
* The snapshot testing example was not using run_beet properly ([`3c933e8`](https://github.com/mcbeet/lectern/commit/3c933e81080a1180b31d2940afca023ac9a7daf3))

## v0.10.0 (2021-04-24)
### Feature
* Add prepend modifier ([`5e1bb1e`](https://github.com/mcbeet/lectern/commit/5e1bb1e81835b8a8aaaedab0f1d2fb138bd3d993))

## v0.9.3 (2021-04-02)
### Fix
* **deps:** Don't use caret to depend on beet because it's not 1.0 yet ([`a97779f`](https://github.com/mcbeet/lectern/commit/a97779fd7bcb22efafeb95b4f383cbd86d61000f))

## v0.9.2 (2021-03-27)
### Fix
* Snapshots shouldn't compare data pack and resource pack names ([`941605b`](https://github.com/mcbeet/lectern/commit/941605b24ef11452e7534af3a7a4bf2597f3f164))

## v0.9.1 (2021-03-24)
### Fix
* Version ranges were weird again ([`bc37fd9`](https://github.com/mcbeet/lectern/commit/bc37fd943021e2d4ab7203f3ac20afb21945d3c4))

## v0.9.0 (2021-03-21)
### Feature
* Update beet and add shader highlighting ([`13e4659`](https://github.com/mcbeet/lectern/commit/13e465995c09a7bc9d974c64e829fca82721fb39))

### Breaking
* `@shader_program` directive renamed to `@shader`  ([`13e4659`](https://github.com/mcbeet/lectern/commit/13e465995c09a7bc9d974c64e829fca82721fb39))

## v0.8.2 (2021-03-19)
### Fix
* Update beet ([`87b0931`](https://github.com/mcbeet/lectern/commit/87b0931c9ec156af4ea468ca27084dd69d92545a))

## v0.8.1 (2021-03-17)
### Fix
* Make the directive comment regex a little more forgiving ([`0471780`](https://github.com/mcbeet/lectern/commit/0471780274e10b3bab2d66d04529af5b269618a4))

## v0.8.0 (2021-03-17)
### Feature
* Add hidden fragments ([`510a213`](https://github.com/mcbeet/lectern/commit/510a2131906257893e23e452dee6336dc38a94eb))

### Fix
* Report line number in error messages ([`c998d68`](https://github.com/mcbeet/lectern/commit/c998d6877c33a91d6ef6a8f9b5cac8dbd0db53dd))
* Take the backticks into account for code fence start line ([`a2c442c`](https://github.com/mcbeet/lectern/commit/a2c442c628ea1087d8f898b9ff504f627070f2f2))

## v0.7.1 (2021-03-09)
### Fix
* Rename get_markdown prefix argument ([`85650fa`](https://github.com/mcbeet/lectern/commit/85650fa930fdeb27b24244b772412e72030b14d3))

## v0.7.0 (2021-03-08)
### Feature
* Add lectern scripts ([`0890b9d`](https://github.com/mcbeet/lectern/commit/0890b9dafd219a4ff9a19698c29def0e1d77e855))
* Add markdown prefetcher ([`e5f65dd`](https://github.com/mcbeet/lectern/commit/e5f65dd0ed01b1066723a176c221627412e12762))
* Add fragment location ([`d79f987`](https://github.com/mcbeet/lectern/commit/d79f987142a1148171cc005aceb6698c2edb564a))
* Enhance pytest explanation ([`8f9b18d`](https://github.com/mcbeet/lectern/commit/8f9b18dbc94e1cd760897826fc30254ad1a4718d))

### Fix
* Accidentally broke emitted filenames ([`5f034b5`](https://github.com/mcbeet/lectern/commit/5f034b59db0cf64fe056650983ae36efeae98f24))
* Lanternmc.com now returns a 403 ([`faaa2d3`](https://github.com/mcbeet/lectern/commit/faaa2d3b26bb1b20b3ae6ad73255edb6e11b0840))

### Documentation
* Document lectern scripts ([`fea9bbf`](https://github.com/mcbeet/lectern/commit/fea9bbf7682cd756022869eccdccd67a67e532d5))
* Document --prefetch-urls ([`4b4eaae`](https://github.com/mcbeet/lectern/commit/4b4eaae89fcd118eab2a3ff9a81cd3f340b4f61b))

## v0.6.1 (2021-03-03)
### Fix
* Make pyright happy ([`f15700c`](https://github.com/mcbeet/lectern/commit/f15700c1c5a5348248ac9947a167fe3931d74c31))

## v0.6.0 (2021-02-27)
### Feature
* Add merge modifier ([`907b630`](https://github.com/mcbeet/lectern/commit/907b630a23bf3f4d88c7a343c529a6a6e2fce07b))
* Add append modifier ([`d4e8be4`](https://github.com/mcbeet/lectern/commit/d4e8be4fb54da6c75b959ce569974b612aedde1a))
* Add base64 modifier ([`acd9d77`](https://github.com/mcbeet/lectern/commit/acd9d7740df3d519b7a19d59f1b98af0d0092d76))

### Fix
* Don't set any cache timeout ([`ebbb5a6`](https://github.com/mcbeet/lectern/commit/ebbb5a6710c8e63fdfe73d9dc7b07848c4ca6818))
* Report unexpected arguments for skip directive ([`f7ff720`](https://github.com/mcbeet/lectern/commit/f7ff720b7444135d888154940f7ed226e0a9dfdb))
* Add item_modifier directive ([`5e034d5`](https://github.com/mcbeet/lectern/commit/5e034d57f36a1f8719e88cd653e7fab8ffbfb5c2))
* Don't cache data url ([`c7517a8`](https://github.com/mcbeet/lectern/commit/c7517a844a3c09da9a448f8742c69f30b9478cc2))

### Documentation
* Udpate readme ([`a110a82`](https://github.com/mcbeet/lectern/commit/a110a823f333f277deff7137f32b133eb2d16ce5))

## v0.5.0 (2021-02-25)
### Feature
* Serialize images ([`7cf6fd9`](https://github.com/mcbeet/lectern/commit/7cf6fd944533a4ea9210f1f795bc4839c1a793de))
* Extract image fragments ([`1c6b71b`](https://github.com/mcbeet/lectern/commit/1c6b71bd0008163226394d77b8909f7459584732))

### Fix
* Use match_tokens() to check for a single code_inline ([`7117521`](https://github.com/mcbeet/lectern/commit/7117521388f5b76e0085d19301d1a9d5d5b7d86f))

## v0.4.0 (2021-02-25)
### Feature
* Add link fragments ([`b0d26d5`](https://github.com/mcbeet/lectern/commit/b0d26d530bd5029ea33bba8b1886a913af6ce125))

## v0.3.2 (2021-02-25)
### Fix
* Patch markdown_it to allow arbitrary data urls ([`bb5c05d`](https://github.com/mcbeet/lectern/commit/bb5c05df7d30e144d014fcaef36c84a802b7c51a))

## v0.3.1 (2021-02-24)
### Fix
* Markdown snapshots now use foldable sections ([`76359e0`](https://github.com/mcbeet/lectern/commit/76359e005ff0f833e0e3a134e78f15089a6dd3ba))

## v0.3.0 (2021-02-24)
### Feature
* Handle folded sections ([`9f611e5`](https://github.com/mcbeet/lectern/commit/9f611e57e766ba3e78bf7a15392fc4ab0e97650a))

## v0.2.2 (2021-02-22)
### Fix
* Resolve output_files relative to the context directory ([`73e4bcd`](https://github.com/mcbeet/lectern/commit/73e4bcdda5be64f5296641a9e66a048aaf35f1d5))

### Documentation
* Add command-line utility help text ([`e615ba1`](https://github.com/mcbeet/lectern/commit/e615ba13b61fc0c1625c538d8290b142d16e3ea3))

## v0.2.1 (2021-02-22)
### Fix
* Handle strip_final_newline in the fragment itself ([`d031607`](https://github.com/mcbeet/lectern/commit/d03160756140dc8fe6406a57869b39780c7f7846))

## v0.2.0 (2021-02-22)
### Feature
* Extract and serialize markdown ([`7827d61`](https://github.com/mcbeet/lectern/commit/7827d61a9fa298da55e05246c294c2a011750017))
* Implement strip_final_newline modifier ([`9aef7d4`](https://github.com/mcbeet/lectern/commit/9aef7d45d0db7b4f7bac667e351b09097e68c2d0))
* Add snapshot testing ([`316e806`](https://github.com/mcbeet/lectern/commit/316e8065a59571722cb0a4bdf2fd38912c818111))
* Add load method ([`81953af`](https://github.com/mcbeet/lectern/commit/81953af678e6e20237cbc7d689775c144ef51f16))

### Fix
* Allow empty modifier ([`c9937b9`](https://github.com/mcbeet/lectern/commit/c9937b96e7b9884027f61dfba719d22692a49d67))
* Don't drop modifier ([`8304433`](https://github.com/mcbeet/lectern/commit/8304433b592b7dd09ca914fd63084fca8cdbecd4))
* Add newline between loot table and advancement in README ([`7337a70`](https://github.com/mcbeet/lectern/commit/7337a70019cd86fa61c33bb212046111419173e8))
* Rename operators to modifiers ([`3886ec3`](https://github.com/mcbeet/lectern/commit/3886ec317b66a50ee0935dec5cb1f72eb3582ccc))

## v0.1.0 (2021-02-22)
### Feature
* Plain text extraction and serialization ([`49e8996`](https://github.com/mcbeet/lectern/commit/49e8996d3398a8683ea91de3df062e47707574c8))

### Fix
* Change document methods and add tests ([`8879b90`](https://github.com/mcbeet/lectern/commit/8879b909c00fa5299793ce90db8c1ee81d2af085))
