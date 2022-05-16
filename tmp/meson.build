project('ihatemeson', ['c'])

srcs = files('main.c')

t = generator(find_program('transform.sh'),
    output: '@BASENAME@.o',
    arguments: ['@INPUT@', '@OUTPUT@']
    )
t_srcs = t.process(srcs)

lol = executable('lol', sources: t_srcs)
