a = 10
b = 20

execute function ~/check:
    if score foo bar matches a.. say hi
    if score foo bar matches ..b say hi
    if score foo bar matches a..b say hi
    if score foo bar matches -b.. say hi
    if score foo bar matches ..-a say hi
    if score foo bar matches -b..-a say hi
    if score foo bar matches a..20 say hi
    if score foo bar matches 10..b say hi
    if score foo bar matches -b..-10 say hi
    if score foo bar matches -20..-a say hi
    if score foo bar matches (a - b).. say hi
    if score foo bar matches ..(a + b) say hi
    if score foo bar matches (a - b)..0 say hi
    if score foo bar matches 0..(a + b) say hi
    if score foo bar matches (a - b)..b say hi
    if score foo bar matches a..(a + b) say hi
    if score foo bar matches (a - b)..(a + b) say hi

execute function ~/check:
    ranges = [
        a..,
        ..b,
        a..b,
        -b..,
        ..-a,
        -b..-a,
        a..20,
        10..b,
        -b..-10,
        -20..-a,
        (a - b)..,
        ..(a + b),
        (a - b)..0,
        0..(a + b),
        (a - b)..b,
        a..(a + b),
        (a - b)..(a + b),
    ]
    for r in ranges:
        if score foo bar matches r say hi
