import numpy as np
# Initialize the grid of Sudoku, each box is represented by a int as binary number of 9 bit. If there is one bit in the number, it meean it is determined
# a totally unknown number is written 111111111, then refining the mask we would deduce that number.

grille=np.zeros((9,9),dtype=np.int16)

# Defining the number for the the number for 1 to 9. 
n1=1
n2=2
n3=4
n4=8
n5=16
n6=32
n7=64
n8=128
n9=256

binarrayvalues=[n1,n2,n3,n4,n5,n6,n7,n8,n9]

# The fill value (perfectly unknown value.
fillvalue=n1|n2|n3|n4|n5|n6|n7|n8|n9


# This set a particular value for a grid
def setValue (x,y,value):
    if value==1:
        grille[x,y]=n1
    elif value==2:
        grille[x,y]=n2
    elif value==3:
        grille[x,y]=n3
    elif value==4:
        grille[x,y]=n4
    elif value==5:
        grille[x][y]=n5
    elif value==6:
        grille[x,y]=n6
    elif value==7:
        grille[x,y]=n7
    elif value==8:
        grille[x,y]=n8
    elif value==9:
        grille[x,y]=n9

def bitcount(n):
    count = 0
    while n > 0:
        count = count + 1
        n = n & (n-1)
    return count


# Retourne le complement de la valeurs si elle est definie, autement retourne le mask passant.
def getMask(i,j):
    mask=fillvalue
    if grille[i,j]&n1==grille[i,j] or grille[i,j]&n2==grille[i,j] \
    or grille[i,j]&n3==grille[i,j] or grille[i,j]&n4==grille[i,j] \
    or grille[i,j]&n5==grille[i,j] or grille[i,j]&n6==grille[i,j] \
    or grille[i,j]&n7==grille[i,j] or grille[i,j]&n8==grille[i,j] \
    or grille[i,j]&n9==grille[i,j]:
        mask=~grille[i,j]
    return mask
    
# Applique le masque uniquement si la valeur n'est pas définie. Si un nombre est trouvé on retourne la veleur True.
# Cela sgnifie qu'il faut mettre à jour les masques des case appartenant à la ligne, à la colonne, au carré
def applyMask(i,j,mask):
#    if i==3 and j==8:
 #       print("ApplyMak",mask)
    if not (grille[i,j]&n1==grille[i,j] or grille[i,j]&n2==grille[i,j] \
    or grille[i,j]&n3==grille[i,j] or grille[i,j]&n4==grille[i,j] \
    or grille[i,j]&n5==grille[i,j] or grille[i,j]&n6==grille[i,j] \
    or grille[i,j]&n7==grille[i,j] or grille[i,j]&n8==grille[i,j] \
    or grille[i,j]&n9==grille[i,j]):
        grille[i,j]=grille[i,j]&mask
        nombretrouve=grille[i,j]&n1==grille[i,j] or grille[i,j]&n2==grille[i,j] \
    or grille[i,j]&n3==grille[i,j] or grille[i,j]&n4==grille[i,j] \
    or grille[i,j]&n5==grille[i,j] or grille[i,j]&n6==grille[i,j] \
    or grille[i,j]&n7==grille[i,j] or grille[i,j]&n8==grille[i,j] \
    or grille[i,j]&n9==grille[i,j]
        return nombretrouve

# Pour chaque ligne calcul et applique le masque créé par les nombre d'une ligne.
def propagateLigneHorizontale(tracage=0):
    for i in range(9):       
        propagateLigneHorizontale1(i,tracage)

# Calcule et applique le masque sur une ligne donnée.
def propagateLigneHorizontale1(i,tracage=0):
    #Pacours toutes la ligne pour calculer les masque a appliquer
    mask=511
    for j in range(9):
        mask=mask&getMask(i,j)
    for j in range(9):
        if applyMask(i,j,mask):
            if tracage==2:print("PropHorizontaleApresTrouve",i,j,getCharForMask(grille[i,j]))
            if tracage:affichegrillehighlight(i,j)
            # Si un nombre a été trouvé, on applique le masque à la ligne verticale, horizontale et le carré associé
            propagateLigneHorizontale1(i,tracage)
            propagateLigneVerticale1(j,tracage)
            propagateSquare1(i//3,j//3,tracage)
            

# Calcul le masque d'une colonne et l'applique le masque pour chaque case
def propagateLigneVerticale(tracage=0):
    for i in range(9):
        propagateLigneVerticale1(i,tracage)

def propagateLigneVerticale1(i,tracage=0):
    mask=511
    for j in range(9):
        mask=mask&getMask(j,i)
#        lignesverticales[i]=mask
    for j in range(9):
        app=applyMask(j,i,mask)
        if app:
            if tracage==2:print("PropVerticaleApresTrouve",j,i,getCharForMask(grille[j,i]),chainebin(grille[j,i]),app)
            if tracage:affichegrillehighlight(j,i)
            # Si un nombre a été trouvé, on applique le masque à la ligne verticale, horizontale et le carré associé
            propagateLigneVerticale1(i,tracage)
            propagateLigneHorizontale1(j,tracage)
            propagateSquare1(j//3,i//3,tracage)
#            print("chainebin03",chainebin(grille[0,4]))

# Pour l'enselbme des carré calculé et appliquer le masque
def propagateSquare(tracage=0):
    for i in range(3):
        for j in range(3):
            propagateSquare1(i,j,tracage)
            #carres[i*3+j]=mask

# Calcul le masque d'une carre et l'applique le masque pour chaque case   
def propagateSquare1(i,j,tracage=0):
    mask=511
    for k in range(3):
        for l in range(3):
            mask=mask&getMask(i*3+k,j*3+l)
    for k in range(3):
        for l in range(3):
            if applyMask(i*3+k,j*3+l,mask):
                if tracage==2:print("PropCarreApresTrouve",i*3+k,j*3+l,getCharForMask(grille[i*3+k,j*3+l]))
                if tracage:affichegrillehighlight(i*3+k,j*3+l)
                # Si un nombre a été trouvé, on applique le masque à la ligne verticale, horizontale et le carré associé
                propagateSquare1(i,j,tracage)
                propagateLigneHorizontale1(i*3+k,tracage)
                propagateLigneVerticale1(j*3+l,tracage)


def debugprint(prefix,i,j,msg=""):
    if i==debugi and j==debugj:
        print(prefix,i,j,":",msg)

#Retourne l'ensemble des valeurs non définie d'un carré
def getCarre(i):
    listCoord=[]
    line=i//3
    col=i%3
    for i in range(line*3,line*3+3):
        for j in range(col*3,col*3+3):
            if not (grille[i,j]&n1==grille[i,j] or grille[i,j]&n2==grille[i,j] \
            or grille[i,j]&n3==grille[i,j] or grille[i,j]&n4==grille[i,j] \
            or grille[i,j]&n5==grille[i,j] or grille[i,j]&n6==grille[i,j] \
            or grille[i,j]&n7==grille[i,j] or grille[i,j]&n8==grille[i,j] \
            or grille[i,j]&n9==grille[i,j]):
                listCoord.append((i,j))
    return listCoord


#Retourne l'ensemble des valeurs non définies de la grille
def getEmptyCells():
    listCoord=[]
    for i in range(9):
        for j in range(9):
            if not (grille[i,j]&n1==grille[i,j] or grille[i,j]&n2==grille[i,j] \
            or grille[i,j]&n3==grille[i,j] or grille[i,j]&n4==grille[i,j] \
            or grille[i,j]&n5==grille[i,j] or grille[i,j]&n6==grille[i,j] \
            or grille[i,j]&n7==grille[i,j] or grille[i,j]&n8==grille[i,j] \
            or grille[i,j]&n9==grille[i,j]):
                listCoord.append((i,j))
    return listCoord

def getThinnerRamification():
    branchMax=9
    nodeRam=None
    for coord in getEmptyCells():
        bits=bitcount(grille[coord])
        if bits<branchMax:
            branchMax=bits
            nodeRam=coord
    return nodeRam

#Retourne l'ensemble des valeurs non définie d'une ligne
def getLigne(i):
    listCoord=[]
    for j in range(9):
        if not (grille[i,j]&n1==grille[i,j] or grille[i,j]&n2==grille[i,j] \
        or grille[i,j]&n3==grille[i,j] or grille[i,j]&n4==grille[i,j] \
        or grille[i,j]&n5==grille[i,j] or grille[i,j]&n6==grille[i,j] \
        or grille[i,j]&n7==grille[i,j] or grille[i,j]&n8==grille[i,j] \
        or grille[i,j]&n9==grille[i,j]):
            listCoord.append((i,j))
    return listCoord

#Retourne l'ensemble des valeurs non définie d'une colonne
def getColumn(j):
    listCoord=[]
    for i in range(9):
        if not (grille[i,j]&n1==grille[i,j] or grille[i,j]&n2==grille[i,j] \
        or grille[i,j]&n3==grille[i,j] or grille[i,j]&n4==grille[i,j] \
        or grille[i,j]&n5==grille[i,j] or grille[i,j]&n6==grille[i,j] \
        or grille[i,j]&n7==grille[i,j] or grille[i,j]&n8==grille[i,j] \
        or grille[i,j]&n9==grille[i,j]):
            listCoord.append((i,j))
    return listCoord

#In each carre we check the possible locations for a number
#if is is unique, then we set this value. Immediatly after doing so the propagation shall be called otherwise it may result in discrepancies.
def infereCarre(tracage=0):
    for ncarre in range(9):
        carre=getCarre(ncarre)
        if len(carre)==1:
            propagateSquare()
            return
        values=[n1,n2,n3,n4,n5,n6,n7,n8,n9]
        for possib in values:
            sum=0
            for coord in carre:
                inc=(grille[coord[0],coord[1]]&possib)
                sum=sum+inc
                if inc>0:
                    foundin=coord
            if sum==possib:
                #print("Trouvé en", foundin,"sur ncarre",ncarre,possib)
                if tracage==2:print("infere carre trouve",foundin,getCharForMask(possib))
                #afficheMaskPossible(carre)
                applyMask(foundin[0],foundin[1],possib)
                if tracage:affichegrillehighlight(foundin[0],foundin[1])
                propagateSquare1(foundin[0]//3,foundin[1]//3,tracage)
                propagateLigneHorizontale1(foundin[0],tracage)
                propagateLigneVerticale1(foundin[1],tracage)
                


#In each line we check the possible locations for a number
#if is is unique, then we set this value. Immediatly after doing so the propagation shall be called otherwise it may result in discrepancies.
def infereLigne(tracage=0):
    for nligne in range(9):
        ligne=getLigne(nligne)
        if len(ligne)==1:
            propagateLigneHorizontale(tracage)
            return
        values=[n1,n2,n3,n4,n5,n6,n7,n8,n9]
        for possib in values:
            sum=0
            for coord in ligne:
                inc=(grille[coord[0],coord[1]]&possib)
                sum=sum+inc
                if inc>0:
                    foundin=coord
            if sum==possib:
          #      print("Trouvé en", foundin,"sur nligne",nligne,possib)
                if tracage==2:print("interfere ligne trouve",foundin,ligne,getCharForMask(possib))
                applyMask(foundin[0],foundin[1],possib)
                if tracage:affichegrillehighlight(foundin[0],foundin[1])
                propagateLigneHorizontale1(foundin[0],tracage)
                propagateLigneVerticale1(foundin[1],tracage)
                propagateSquare1(foundin[0]//3,foundin[1]//3,tracage)                            

#In each column we check the possible locations for a number
#if is is unique, then we set this value. Immediatly after doing so the propagation shall be called otherwise it may result in discrepancies.
def infereColumn(tracage=0):  
    for ncolumn in range(9):
        column=getColumn(ncolumn)
        if len(column)==1:
            propagateLigneVerticale(tracage)
            return
        values=[n1,n2,n3,n4,n5,n6,n7,n8,n9]
        for possib in values:
            sum=0
            for coord in column:
                inc=(grille[coord[0],coord[1]]&possib)
                sum=sum+inc
                if inc>0:
                    foundin=coord
            if sum==possib:
                if tracage==2:print("infere vertical trouve",foundin,getCharForMask(possib),values,len(column))
         #       print("Trouvé en", foundin,"sur ncolumn",ncolumn,possib)
                applyMask(foundin[0],foundin[1],possib)
                if tracage:affichegrillehighlight(foundin[0],foundin[1])
                propagateLigneVerticale1(foundin[1],tracage)
                propagateLigneHorizontale1(foundin[0],tracage)
                propagateSquare1(foundin[0]//3,foundin[1]//3,tracage)                            


# Compte le nombre de case de la grille dont la valeur n'est pas encore affectee.
# Cela permet de determiner si la grille est remplie ou pas et servira de condition d'arrêt.
def compteNombreCaseVide():
    compte=0
    for i in range(9):
        for j in range(9):
            if grille[i,j]&n1==grille[i,j] or grille[i,j]&n2==grille[i,j] \
            or grille[i,j]&n3==grille[i,j] or grille[i,j]&n4==grille[i,j] \
            or grille[i,j]&n5==grille[i,j] or grille[i,j]&n6==grille[i,j] \
            or grille[i,j]&n7==grille[i,j] or grille[i,j]&n8==grille[i,j] \
            or grille[i,j]&n9==grille[i,j]:
                compte=compte+1
    return 9*9-compte
                

# This method is a step to resolve. It first propagate the masks of line, columns and squares.
# Then apply inferences to guess some cells. Depending on the difficulty of a Sudoku, there could be several iterations.
def resolutionstep(tracage=0):
    propagateLigneHorizontale(tracage)
    propagateLigneVerticale(tracage)
    propagateSquare(tracage)
    infereCarre(tracage)
    infereLigne(tracage)
    infereColumn(tracage)


# The resolution perform as many step as it is required to resolve the Sodoku.
# for the difficult sudoku, when a tree needs to be explored, this methos also do some attempts
def resolution(decisions,tracage=0):
    grilleStack=[]
    maxIteration = 9*9
    iterationCount=0
    casesVides=compteNombreCaseVide()
    while casesVides>0 and iterationCount<maxIteration:
        #print("Tracage",tracage)
        resolutionstep(tracage)
        iterationCount=iterationCount+1
        compteApresIteration=compteNombreCaseVide()
        if compteApresIteration==casesVides:
            iterationCount=maxIteration           
        casesVides=compteApresIteration   
    if iterationCount==maxIteration:
        cell=getThinnerRamification()
        return exploArbre(cell,decisions)  
    else:
        print("Résolu en",iterationCount, "itérations",decisions)
        return True

#
def replay(decisions,tracage):
    decisions.reverse()
    grilleStack=[]
    maxIteration = 9*9
    iterationCount=0
    casesVides=compteNombreCaseVide()
    while casesVides>0 and iterationCount<maxIteration:
        resolutionstep(tracage)
        iterationCount=iterationCount+1
        compteApresIteration=compteNombreCaseVide()
        if compteApresIteration==casesVides:
            iterationCount=maxIteration           
        casesVides=compteApresIteration   
    if iterationCount==maxIteration:
        decision=decisions.pop()
        grille[decision[0]]=decision[1]
        affichegrillehighlight(decision[0][0],decision[0][1],1)
        replay(decisions,tracage)
    else:
        print("Résolu en",iterationCount, "itérations",decisions)
        return True
    
    
        
# For a given cells, it enumerate the possible value that can be taken and used as asumtionx.
def getGetOptions(x):
    options=[]
    for i in binarrayvalues:
        if x&i:
            options.append(i)
    return options

# Check is a grid is valid i.e. if a criteria of the sudoku is violated
# In only checks wether a line has a dupplicate number, but it also 
# demonstrate with the same criteria that no column has duplicate.
def checkValid():
    for i in range(9):
        a=0
        for j in range(9):
           a=a|grille[i,j] 
        if a!=511:
            return False
    return True

# For the given cell, we explore the various options. This method is reccuring, meaning, if another branching is needed, it will also be explored.
# the exploration will return True if the exploration lead to a valid grid. Il will retur false otherwise.
def exploArbre(cell,decisions):
    global grille
    grillestoexplore=[]
    for option in getGetOptions(grille[cell]):
        grilletoexplore=grille.copy()
        grilletoexplore[cell]=option
        grillestoexplore.append(grilletoexplore)
    
    for grilletoexplore in grillestoexplore:
        grille=grilletoexplore
        res = resolution(decisions)
        if res:
            if checkValid():
                print("Happy end", cell,grille[cell])
                decisions.append((cell,grille[cell]))
                print(decisions)
                return True
            else:
                print("Pas bon")
        else:
            cell=getThinnerRamification()
            print("On continue l'exploration",cell)
            return exploArbre(cell)


def resolutionetreplay():
    global grille
    grilleforreplay=grille.copy()
    decisions=[]
    resolution(decisions,0)
    grille=grilleforreplay.copy()
    tracage=1
    print("Commencement du replay")
    replay(decisions,1)



#Diplay a grid
def affichegrille():
    print("===========")
    for i in range (9):
        if i==3 or i==6:
            print("------------")
        for j in range (9):
            if j==3 or j==6:
                print ('|', end='')
            if grille[i,j]&n1==grille[i,j]:
                print ("1", end='')
            elif grille[i,j]&n2==grille[i,j]:
                print ("2", end='')
            elif grille[i,j]&n3==grille[i,j]:
                print ("3", end='')
            elif grille[i,j]&n4==grille[i,j]:
                print ("4", end='')
            elif grille[i,j]&n5==grille[i,j]:
                print ("5", end='')
            elif grille[i,j]&n6==grille[i,j]:
                print ("6", end='')
            elif grille[i,j]&n7==grille[i,j]:
                print ("7", end='')
            elif grille[i,j]&n8==grille[i,j]:
                print ("8", end='')
            elif grille[i,j]&n9==grille[i,j]:
                print ("9", end='')
            else:
                print (" ", end='')
        print('')
    print("===========")


#Diplay a grid
def affichegrillehighlight(hi,hj,choix=0):
    print("===========")
    for i in range (9):
        if i==3 or i==6:
            print("------------")
        for j in range (9):
            if j==3 or j==6:
                print ('|', end='')
            if i==hi and j==hj:
                if choix:
                    #print ('\x1b[31m\u001b[47m', end='')           
                    print ('\x1b[31m', end='')           
                else:
                    #print ('\x1b[32m\u001b[47m', end='')           
                    print ('\x1b[32m', end='')           
            if grille[i,j]&n1==grille[i,j]:
                print ("1", end='')
            elif grille[i,j]&n2==grille[i,j]:
                print ("2", end='')
            elif grille[i,j]&n3==grille[i,j]:
                print ("3", end='')
            elif grille[i,j]&n4==grille[i,j]:
                print ("4", end='')
            elif grille[i,j]&n5==grille[i,j]:
                print ("5", end='')
            elif grille[i,j]&n6==grille[i,j]:
                print ("6", end='')
            elif grille[i,j]&n7==grille[i,j]:
                print ("7", end='')
            elif grille[i,j]&n8==grille[i,j]:
                print ("8", end='')
            elif grille[i,j]&n9==grille[i,j]:
                print ("9", end='')
            else:
                print (" ", end='')
            if i==hi and j==hj:
                print ('\x1b[0m', end='')           
        print('')
    print("===========")

#Affiche les mask des cellules dons les coordonnées sont passées en argument
def afficheMaskPossible(cells):
    for i in cells:
        displaybingrille(i[0],i[1])


#Affiche la représentation binaire d'un nombre.
def chainebin(x):
    chaine=""
    if x&n1:
        chaine=chaine+"1"
    else:
        chaine=chaine+"0"
    if x&n2:
        chaine=chaine+"1"
    else:
        chaine=chaine+"0"
    if x&n3:
        chaine=chaine+"1"
    else:
        chaine=chaine+"0"
    if x&n4:
        chaine=chaine+"1"
    else:
        chaine=chaine+"0"
    if x&n5:
        chaine=chaine+"1"
    else:
        chaine=chaine+"0"
    if x&n6:
        chaine=chaine+"1"
    else:
        chaine=chaine+"0"
    if x&n7:
        chaine=chaine+"1"
    else:
        chaine=chaine+"0"
    if x&n8:
        chaine=chaine+"1"
    else:
        chaine=chaine+"0"
    if x&n9:
        chaine=chaine+"1"
    else:
        chaine=chaine+"0"
    return chaine
        
def displaybin(x):
    print(chainebin(x))

def displaybingrille(i,j):
    displaybin(grille[i,j])

# Retroune le caractère qui conrespond à un chiffre, X si le nombre n'est pas encore determiné
def getCharForMask(item):
    if item&n1==item:
        return '1'
    elif item&n2==item:
        return '2'
    elif item&n3==item:
        return '3'
    elif item&n4==item:
        return '4'
    elif item&n5==item:
        return '5'
    elif item&n6==item:
        return '6'
    elif item&n7==item:
        return '7'
    elif item&n8==item:
        return '8'
    elif item&n9==item:
        return '9'
    else:
        return "X"





# Grille 128 initialize the grid
def samplegridinitdemoniaque2():
    #Initialise la grille avec toutes les valeurs possible.
    grille.fill(fillvalue)
    setValue(0,3,4)
    setValue(0,5,9)
    setValue(0,7,8)
    setValue(0,8,6)
    setValue(1,1,6)
    setValue(1,7,4)
    setValue(1,8,7)
    setValue(2,0,1)
    setValue(2,1,2)
    setValue(3,0,3)
    setValue(3,2,5)
    setValue(3,3,7)
    setValue(4,6,6)
    setValue(4,7,7)
    setValue(5,3,3)
    setValue(6,0,6)
    setValue(6,3,9)
    setValue(6,6,4)
    setValue(7,0,8)
    setValue(7,4,1)
    setValue(7,7,2)
    setValue(8,3,5)

# Grille 47 initialize the grid
def samplegridinitdemoniaque():
    #Initialise la grille avec toutes les valeurs possible.
    grille.fill(fillvalue)
    setValue(0,0,5)
    setValue(0,4,9)
    setValue(0,5,6)
    setValue(0,8,7)
    setValue(1,0,3)
    setValue(2,1,8)
    setValue(2,3,2)
    setValue(2,5,7)
    setValue(2,7,9)
    setValue(3,0,8)
    setValue(3,3,4)
    setValue(3,4,5)
    setValue(4,1,7)
    setValue(4,6,8)
    setValue(5,2,4)
    setValue(5,5,3)
    setValue(5,7,1)
    setValue(6,2,8)
    setValue(6,8,5)
    setValue(7,4,6)
    setValue(8,1,6)
    setValue(8,4,4)
    setValue(8,8,1)

# Grille 47 initialize the grid
def samplegridinitdifficile():
    #Initialise la grille avec toutes les valeurs possible.
    grille.fill(fillvalue)
    setValue(0,1,5)
    setValue(0,2,1)
    setValue(0,3,7)
    setValue(0,4,3)
    setValue(1,0,6)
    setValue(1,2,3)
    setValue(2,8,4)
    setValue(3,0,7)
    setValue(3,1,8)
    setValue(3,6,5)
    setValue(3,8,9)
    setValue(4,5,6)
    setValue(4,7,2)
    setValue(4,8,7)
    setValue(5,1,3)
    setValue(5,4,2)
    setValue(6,0,9)
    setValue(6,4,5)
    setValue(6,6,7)
    setValue(7,1,7)
    setValue(7,5,8)
    setValue(8,6,2)
    setValue(8,7,4)

# Grille 50 initialize the grid
def samplegridinitmedium():
    #Initialise la grille avec toutes les valeurs possible.
    grille.fill(fillvalue)
    setValue(0,1,6)
    setValue(0,5,7)
    setValue(0,8,5)
    setValue(1,4,2)
    setValue(1,7,8)
    setValue(1,8,4)
    setValue(2,1,4)
    setValue(2,7,3)
    setValue(3,1,2)
    setValue(4,0,6)
    setValue(4,1,8)
    setValue(4,5,1)
    setValue(4,6,3)
    setValue(5,0,9)
    setValue(5,2,7)
    setValue(5,6,4)
    setValue(6,3,2)
    setValue(6,4,3)
    setValue(6,6,9)
    setValue(7,0,1)
    setValue(7,2,3)
    setValue(7,4,9)
    setValue(8,2,8)
    setValue(8,4,4)

# Grille 57 initialize the grid
def samplegridiniteasy():
    #Initialise la grille avec toutes les valeurs possible.
    grille.fill(fillvalue)
    setValue(0,0,8)
    setValue(0,4,1)
    setValue(0,5,7)
    setValue(0,6,5)
    setValue(0,8,2)
    setValue(1,2,6)
    setValue(1,4,2)
    setValue(1,7,8)
    setValue(1,8,4)
    setValue(2,1,5)
    setValue(2,2,2)
    setValue(2,4,8)
    setValue(2,5,4)
    setValue(3,0,6)
    setValue(3,4,9)
    setValue(3,6,1)
    setValue(3,7,4)
    setValue(4,1,2)
    setValue(5,0,7)
    setValue(5,4,4)
    setValue(5,5,5)
    setValue(5,8,3)
    setValue(6,6,4)
    setValue(6,7,2)
    setValue(7,0,4)
    setValue(7,1,6)
    setValue(7,5,1)
    setValue(7,6,9)
    setValue(7,8,8)
    setValue(8,2,9)
    setValue(8,3,4)
    setValue(8,4,5)
    setValue(8,5,8)
    setValue(8,8,7)

