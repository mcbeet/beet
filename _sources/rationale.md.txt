# Rationale

Data packs and resource packs were introduced by Mojang to make hard-coded logic data-driven. This turned Minecraft into an incredible parametric sandbox, where most aspects of the vanilla experience can be overridden at will by players. As a result, data packs and resource packs naturally became the primary entry point for customizing Minecraft and over time, they gained an impressive number of features that now make it possible to implement almost any game mechanic imaginable using a resource pack and a data pack.

However, by design, Minecraft packs are not meant to be ergonomic for developers in the technical community. The format is constrained by the following requirements:

- Data packs and resource packs should be simple and easily loadable by Minecraft. Mojang could introduce features targeted to developers to make their lives easier but it would affect loading times for all players. This means that there's an upper bound when it comes to complexity.
- Data packs and resource packs should be interoperable. Minecraft needs to be able to combine and merge resources from multiple packs, and the "simplicity constraint" limits the affordable strategies for doing that.

This results in a simple and straightforward distribution format that happens to be pretty easily approachable despite not being optimized for developer experience.

## Data pack tooling

As creators become more and more ambitious, data packs become harder and harder to reason about due to the very limited abstractions available. The community is tackling the problem with tooling that alleviates some of the common use-cases. The ecosystem flourished with tons of generators, and a wide variety of projects from command pre-processors to frameworks of all kinds and full-blown programming languages.

The problem is that these efforts are mostly disparate, and some of these tools end up having to re-implement the same things to develop their value proposition.

It's also important to understand that they all have their strength and weaknesses and that depending on your use case some tools will provide more suitable abstractions than others. However, it's usually pretty difficult to use them together because the interoperability is generally quite poor due to the different toolchains. As a result, creators often need to compromise when a combination of tools would provide the ideal workflow.

## What's a development kit for data packs anyway?

The term "development kit" is technically the most accurate way to describe `beet` but it sounds slightly obscure. Since you can't directly map the term "development kit" to a specific use case it can take some time to wrap your head around it. Projects with a more bounded scope like "command pre-processor" or "framework for writing commands in TypeScript" are easier to grasp because they address a specific high-level need. `beet` is a level below that. It's a platform on top of which you can build and integrate any of the tools or frameworks you might need to streamline pack development.

One analogy would be with the Java SDK. When you want to make programs in Java you install the JDK (Java Development Kit) which contains your standard library as well as tools for building your projects. `beet` is similar. The library contains primitives for working with data packs and resource packs programmatically, and you use the `beet` toolchain to build your projects.

In practice, this means that `beet` is here to introduce a build step and rescue you from developing directly in your `.minecraft` folder. By default, the `beet` pipeline is a simple pass-through. You tell it to load your data pack and resource pack and it will output it in your development world or wherever you want. Even without introducing any new concept compared to regular data pack development, it's already much more ergonomic since you can have your data pack and resource pack side by side in the same directory under version control. It also lets you easily experiment with different worlds, and even benefit from live data pack reloading with the `beet watch --reload` command.

Of course, the whole point of introducing a build step is that after loading your data pack, it lets you do more stuff. For example, it can help you automate releases and versioning now that there's a clear separation between your project sources and what you're going to publish.

## A unified build process

Data packs aren't optimized for developer experience so you often end up having to write a lot of repetitive code or use external generators. Depending on your use case, you may already have custom scripts that let you automate things. This quickly becomes a nightmare to maintain, and it clutters your workspace by making you navigate through lots of files that you wouldn't even edit manually anyway. `beet` makes it easy to make your project data-driven by letting you write plugins that operate on the output data pack and resource pack. You can think of the `beet` pipeline as a little conveyor belt that transports your data pack through a factory. Along the way, plugins can analyze, apply transformations, and generate anything that you wouldn't want to write manually.

The plugin system is also what makes it possible to write higher-level tools and integrate external utilities into your build process. The `beet` ecosystem has been growing steadily and there are now really useful projects like [`mecha`](https://github.com/mcbeet/mecha) and [`lectern`](https://github.com/mcbeet/lectern) that leverage `beet` to extend the command syntax and provide a document-based authoring format for data packs and resource packs.

The core idea behind the `beet` pipeline is that since different projects can have widely different requirements, it should be able to act as an interoperability layer between existing tools to let you set up a cohesive build system without compromising. This is implemented through merging by using data packs as a sort of "lingua franca" emitted and understood by pretty much everything built by the community.

If you're familiar with web development, you could compare `beet` to `webpack` in the sense that it lets you process and bundle separate sources into a production package. For example, `beet` integrates with [`sandstone`](https://www.sandstone.dev/), which is a Node.js/TypeScript framework for writing commands. `beet` can run `sandstone` as part of your build and merge the generated data pack with anything else you might need.

Another implication of the unified pipeline is that new utilities don't need to reinvent the wheel. They can leverage the toolchain and `beet` primitives to simplify their implementation. It also makes it easier for the end-user thanks to the seamless interoperability and the friendly development workflow.
