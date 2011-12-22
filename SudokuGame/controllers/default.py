# -*- coding: utf-8 -*- 

response.title = "Sudoku solver"
response.subtitle = "powered by web2py"

def index():
    session.grid=None
    return dict()

def callback():
    import copy
    sudoku = local_import('sudoku')
    if request.vars.reset:
        session.grid=None
    if not session.grid: session.grid=[[0 for i in range(9)] for j in range(9)]
    try:
        a,b,command=-1,-1,''
        for key in request.vars:
            a,b = int(key[1]),int(key[2])
            session.grid[a][b] = int(request.vars[key] or 0)
        solutions = sudoku.solve_sudoku((3, 3), copy.deepcopy(session.grid))
        for solution in solutions:
            for i in range(9):
                for j in range(9):
                    if (i,j)!=(a,b) and not session.grid[i][j]:
                        command+="jQuery('#x%s%s').val('%s');" % (i,j,solution[i][j] or '')
            break
    except Exception, e:
        command='' 
    if not command:
        for i in range(9):
            for j in range(9):
                if (i,j)!=(a,b) and not session.grid[i][j]:
                    command+="jQuery('#x%s%s').val('').css('color','gray');" % (i,j)
    return command


