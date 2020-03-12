import copy

#obtiene las restricciones de una
#casilla dada su posicion en el
#tablero
def getConstraints(i,j,board):
  constraints=[[],[],[]]
  constraints[0],constraints[1]=getRowColCons(i,j,board)
  constraints[2]=getQuadrantCons(i,j,board)
  return constraints

#restricciones de filas y columnas
def getRowColCons(i,j,board):
  constraints=[[],[]]
  for x in range(0,9):
    if(board[i][x]!=0 and x!=j):
      constraints[0].append(board[i][x])
    if(board[x][j]!=0 and x!=i):
      constraints[1].append(board[x][j])
  return constraints[0],constraints[1]

#restriccion del Cuadrante
def getQuadrantCons(i,j,board):
  constraints=[]
  for indexi in range(0,3): 
    for indexj in range(0,3):
      if(board[i//3*3+indexi][j//3*3+indexj]!=0 and not (indexi==i and indexj==j)):
        constraints.append(board[i//3*3+indexi][j//3*3 +indexj])
  return constraints

#Establece el dominio inicial
# para las 81 celdas
def setDomain(board):
  domain=[[[] for i in range(9)] for i in range(9)]
  #En este ciclo establecemos las casillas
  #con valores fijos y se hace el supesto
  #que las demas casillas toman valores de 1 a 9
  i=0
  for line in board:
    j=0
    for box in line:    
      if(box!=0):
        domain[i][j]=[box]
      else:
        domain[i][j]=[1,2,3,4,5,6,7,8,9]
      j=j+1
    i=i+1

  #En este ciclo se aplican las restricciones
  #a todas las casillas reduciendo el dominio
  #de cada celda
  i=0
  for line in board:
    j=0
    for box in line:    
      if(box==0):
        constraints=getConstraints(i,j,board)
        domain[i][j]=[x for x in domain[i][j] if x not in constraints[0]]
        domain[i][j]=[x for x in domain[i][j] if x not in constraints[1]]
        domain[i][j]=[x for x in domain[i][j] if x not in constraints[2]]
      j=j+1
    i=i+1
  return domain

#se busca la variable mas restringida
#teniendo en cuenta los valores que puede tomar(dominio)
def mostRestricted(board,domain):
  restriction=1000
  variables=[]
  i=0
  for line in board:
    j=0
    for box in line:    
      if(box==0):
        if(restriction>len(domain[i][j])):
          restriction=len(domain[i][j])
          variables.clear()
          variables.append((i,j))  
        elif(restriction==len(domain[i][j])):
          variables.append((i,j))  
      j=j+1
    i=i+1
  return variables

#variable menos restrictora manejo -404 como
#codigo de error
def leastRestrictiveVariable(board,domain,VMR):
  value=-404
  best=(-1,-1)
  conflicts=32
  for box in VMR:
    a,b=box
    for x in domain[a][b]:
      temp=calculateConflitcs(box,x,board,domain)
      if(temp<conflicts):
        conflicts=temp
        best, value=(copy.deepcopy(a),copy.deepcopy(b)), copy.deepcopy(x)
  return best,value

#calcula los confictos al poner el atributo value
#en las coordenada box
def calculateConflitcs(box,value,board,domain):
  i,j=box
  eye=set()
  #eye=[]
  for x in range (0,9):
    if(board[i][x]==0 and x!=j):
      if value in domain[i][x]:
        #eye.append({i,x})
        eye.add(frozenset({i,x}))
    if(board[x][j]==0 and x!=i):
      if value in domain[x][j]:
       #eye.append({x,j})
       eye.add(frozenset({x,j}))
  for indexi in range(i//3,i//3+3):
    for indexj in range(j//3,j//3+3):
      if(board[indexi][indexj]==0 and not (indexi==i and indexj==j)):
        if value in domain[indexi][indexj]:
          #eye.append({indexi,indexj})
          eye.add(frozenset({indexi,indexj}))
  #print(len(eye),count)
  #print(len(eye))
  return len(eye)
  

#Funcion Principal
#aplica el backtraking y correccion
def backtrakingcore(domain,board):
  printboard(board)
  #es una solucion?
  if isSolution(board):
    return True
  else:
    result=False
    while not result:
      #busca VMR y VLR
      VMR=mostRestricted(board,domain)
      VLR=leastRestrictiveVariable(board,domain,VMR)
      #si es imvalido regreso falso
      if(VLR[1]==-404):
        print("REGRESO BUSCANDO SOLUCIONES",file=f)
        return False
      else:
        newboard=copy.deepcopy(board)
        x,y=VLR[0]
        newboard[x][y]=VLR[1]
        #calculo el impacto en el dominio
        newdomain=updateDomain(x,y,VLR[1],domain,newboard)
        #verifico deja sin opciones a alguna casilla
        dontTry=False
        if  [] in newdomain:
            dontTry=True
        #si todo esta bien sigo con los llamados recursivos
        if not dontTry:
            print("VMR",VMR,file=f)
            print("VLR",VLR,file=f)
            printboardf(newboard)
            result=backtrakingcore(newdomain,newboard)
        #reseteo casilla y remuevo el valor
        #probado anteriormente del dominio
        newboard[x][y]=0
        domain[x][y].remove(VLR[1])
        #sino no hubo un resultado exitoso
        #pruebo con las demas opciones del
        #VLR
        if not result:
            for anotherOption in  domain[x][y]:
                print("intento con ",anotherOption," VLR ",VLR[0] )
                newboard[x][y]=anotherOption
                printboard(newboard)
                newdomain=updateDomain(x,y,anotherOption,domain,newboard)
                if [] in newdomain:
                    print("REGRESO BUSCANDO SOLUCIONES",file=f)
                    return False 
                print("VMR",VMR,file=f)
                print("VLR",[VLR[0],anotherOption],file=f)
                printboardf(board)
                result=backtrakingcore(newdomain,newboard)
                newboard[x][y]=0
                if result:
                    return True
        #print(result)
        return result

#actualiza el dominio se usa generalmente
#para enviarlo como parametro al prox. llamado
def updateDomain(i,j,value,domain,board):
  newdomain=copy.deepcopy(domain)
  newdomain[i][j]=[value]
  for index in range(0,9):
    #actualizar dominio de columna
    if index!=i:
      newdomain[index][j]=[x for x in newdomain[index][j] if x!=value]
    #actualizar dominio de fila
    if index!=j :
      newdomain[i][index]=[x for x in newdomain[i][index]if x!=value]
  #actualizar dominio de region
  for indexi in range(0,3): 
    for indexj in range(0,3):
        if(indexi!=i and indexj!=j):
            newdomain[i//3*3+indexi][j//3*3 +indexj]=[x for x in newdomain[i//3*3+indexi][j//3*3 +indexj]if x!=value]
  return newdomain

#verifica si el tablero encontro una solucion
def isSolution(board):
  for i in range(0,9):
    row=[]
    column=[]
    for j in range(0,9):
      if(board[i][j]==0):
        return False
      if(board[i][j] not in row):
        row.append(board[i][j])
      else:
        return False
      if(board[j][i] not in column):
        column.append(board[j][i])
      else:
        return False
  return True

#dibuja el tablero
def printboard(board):  
  for x in board:
    for value in x:
      print(value,end="|")
    print()
  print()

#dibuja el tablero
# en el archivo
def printboardf(board):
  i=0
  for line in board:
      if(i%3==0):
          print("------------------------------",file=f)
      print(line[0:3],line[3:6],line[6:9],file=f)
      i=i+1
  print("------------------------------",file=f)

#pre-preparacion y llamado
def solve(board):
  domain=setDomain(board)
  return backtrakingcore(domain,board)

#recibe un archivo y lo convierte
# a una matriz de listas
#########################
###  EN CONSTRUCCION  ###
#########################
def filetomatrix(filename):
  readfile=open(filename,'r')
  board=[[[] for i in range(9)] for i in range(9)]
  line = readfile.readline()
  row=0
  while line:
    stringData=line.split(",")
    for column in range(0,9):
      board[row][column]=int(stringData[column])
    line=readfile.readline()
    row=row+1
  return board


#################################
### RUTA DEL ARCHIVO   ##########
#################################
board=filetomatrix("board2.txt")
f = open("resultados.txt","w")
printboardf(board)
s=solve(board)
print("solucionado:",s)
if not s:
  print("NO EXISTEN SOLUCIONES",file=f)
