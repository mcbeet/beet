# Changelog

<!--next-version-placeholder-->

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