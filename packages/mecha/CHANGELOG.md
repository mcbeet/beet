# Changelog

<!--next-version-placeholder-->

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