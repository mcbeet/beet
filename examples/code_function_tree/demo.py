from beet import Context, Function, TreeNode


def beet_default(ctx: Context):
    for node, function in ctx.generate.function_tree("abcdef"):
        handle_content(ctx, node, function, 2)

    for node, function in ctx.generate.function_tree("abcdef", key=ord):
        handle_content(ctx, node, function, 3)

    for node, function in ctx.generate.function_tree("{hash}", "abcdef", key=ord):
        handle_content(ctx, node, function, 4)

    for node, function in ctx.generate.function_tree("abcdef", name="something"):
        handle_content(ctx, node, function, 2)


def handle_content(ctx: Context, node: TreeNode[str], function: Function, n: int):
    if node.root:
        ctx.generate(Function([f"function {node.parent}"], tags=["minecraft:tick"]))
        function.lines.append(f"scoreboard players add #index temp 1")
    if node.partition(n):
        function.lines.append(f"execute if score #index temp matches {node.range} run function {node.children}")
    else:
        function.lines.append(
            f"execute if score #index temp matches {node.range} run say {node.value}"
        )
