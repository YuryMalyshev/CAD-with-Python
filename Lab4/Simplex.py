
#TODO: impement priority. First check for most neative in X values, if there is one - take it, if not check the whole row.



import numpy as np;
import math;
import csv;
class Simplex:
    
    initialMatrix = [];
    initialDirectives = [];
    solutionMatrix = [];
    
    def __init__(self, filename):
        print("Init. Filename = " + filename);
        self.initialDirectives, self.initialMatrix = Simplex.readFile(filename);
        self.fixDirective();
        print(self.initialDirectives);
        Simplex.printArray(self.initialMatrix);
    
    def fixDirective(self):
        print("max of initial matrix" + str(np.max(self.initialMatrix)));
        i = 0;
        for d in self.initialDirectives:
            if(d == "max"):
                if(np.max(self.initialMatrix[i]) <= 0):
                    print("It was max");
                    self.initialMatrix[i] *= -1;
                    self.initialDirectives[i] = "min";
                    break;
            elif(d == "min"):
                if(np.max(self.initialMatrix[i]) <= 0):
                    print("It was min");
                    self.initialMatrix[i] *= -1;
                    self.initialDirectives[i] = "max";
                    break;
            i += 1;
                    

    
    def solve(self):
        print("Solving using simplex...");
        t_matrix, t_directives = self.checkObjective();
        t_matrix, t_directives = self.correctSigns(t_matrix, t_directives);
        self.solutionMatrix = self.correctSurplus( t_matrix, t_directives );
        self.solutionMatrix = self.maximize(self.solutionMatrix);
        #self.roundSolution(self.solutionMatrix);
        print("="*25 + "Final Result" + "="*25 + "\n");
        Simplex.printArray(self.solutionMatrix);
        print("="*62);
        
    def showResultValues(self, matrix):
        solutionArray = [];
        if(self.initialDirectives[-1] == "max"):
            col = 0;
            while (col < len(matrix[0])-1):
                isNotZero, row = self.hasOne(matrix[:, col]);
                if(isNotZero):
                    solutionArray.append(matrix[row][col] * matrix[row][-1]);
                else:
                    solutionArray.append(0);
                col += 1;
        elif(self.initialDirectives[-1] == "min"):
            i = 0;
            for el in matrix[-1, :-1]:
                i+= 1;
                if(i < len(self.initialMatrix)):
                    solutionArray.append(el);
                else:
                    solutionArray.insert(i - len(self.initialMatrix),el);
        else:
            print("Objective was not defined!");
            return;
        i = 0;
        print("Solution is:");
        for el in solutionArray:
            i += 1;
            if(i < len(self.initialMatrix[0])):
                print("x" + str(i) + ": " + str(el));
            else:
                print("s" + str(i - ( len(self.initialMatrix[0]) -1 ) ) + ": " + str(el) );
    
    def hasOne(self, array):
        index = -1;
        count = 0;
        i = 0;
        for el in array:
            if(el != 0):
                count += 1;
                index = i;
                if(count > 1):
                    return False, index;
            i += 1;
        return True, index;
                
    def checkObjective(self):
        matrix = np.copy(self.initialMatrix);
        directives = np.copy(self.initialDirectives);
        if directives[-1] == "min":
            for i in range(matrix.shape[0]):
                if directives[i] == "leq":
                    matrix[i] = np.multiply(matrix[i], -1.);
            temp = [];
            matrix = np.transpose(matrix);
            for i in range(1,matrix.shape[0]):
                temp.append("leq");
            temp.append("max");
            directives = temp;
        return matrix, directives;
    
    def correctSigns(self, matrix, directives):
        matrix[-1] = np.multiply(matrix[-1], -1.);
        for i in range(matrix.shape[0]-1):
            if matrix[i, -1] < 0.:
                if directives[i] == "geq":
                    directives[i] = "leq";
                elif directives[i] == "leq":
                    directives[i] = "geq";
                matrix[i] = np.multiply(matrix[i], -1.);
        return matrix, directives;
                
    def correctSurplus(self, matrix, directives):
        s = np.zeros((matrix.shape[0], matrix.shape[0]-1), dtype=np.float32);
        for i in range(matrix.shape[0]-1):
            if directives[i] == "leq":
                s[i, i] = 1;
            else:
                s[i,i] = -1;
        matrix = np.insert(matrix, [matrix.shape[1]-1], s, axis=1);
        return matrix;
    
    @staticmethod   
    def divideArrays(array1, array2): #divides array1 by array2. If value in array2 <= 0 -> result = infinity
        temp = np.zeros(len(array1));
        i = 0;
        for x in array2:
            if( x <= 0 ):
                temp[i] = math.inf;
            else:
                temp[i] = array1[i]/array2[i];
            i += 1;
        return temp;
    
    def maximize(self, matrix): 
        while(min(matrix[-1]) < 0):
            print("Starting a new iteration with the following matrix: ");
            Simplex.printArray(matrix);
            entryColumn = np.argmin(matrix[-1]);            
            if(all ( matrix[:,entryColumn] < 0)):
                print("All values are negative. This is an unbounded problem");
                INF = math.inf;
                if(self.initialDirectives[0] == "min"):
                    INF *= -1;
                matrix[-1,-1] = INF;              
                return matrix;
            temp = Simplex.divideArrays(matrix[0:-1, -1] , matrix[0:-1, entryColumn]);
            entryRow = np.argmin(temp);
            print("Pivot point is at: [" + str(entryRow) + ";" + str(entryColumn) + "]");
            matrix = Simplex.performElimiation(matrix, entryRow, entryColumn);
            #self.roundSolution(matrix);
            print();
        return matrix;
       
    def roundSolution(self, matrix, digits=6):
        for i in range(matrix.shape[0]):
            for j in range(matrix.shape[1]):
                matrix[i][j] = round(matrix[i][j], digits);
        return matrix;
    
    @staticmethod
    def printArray(matrix):
        for row in matrix:
            line = "  [";
            for el in row:
                line = line + "%7.2f " % (el);
            line = line + "]";
            print(line);
        print();
    
    @staticmethod
    def readFile(filepath):
        with open(filepath) as file:
            reader = csv.reader(file, delimiter=",");
            matrix = [];
            obj_fun = [];
            objective = None;
            directives = [];

            for row in reader:
                line = [];
                for el in row[1:]:
                    line.append(float(el));
                if(row[0] == "min" or row[0] == "max"):
                    obj_fun = line;
                    objective = row[0];
                else:
                    directives.append(row[0]);
                    matrix.append(line);

            matrix.append(obj_fun);
            directives.append(objective);
            matrix = np.asarray(matrix);
            
            return directives, matrix;
       
    @staticmethod
    def performElimiation(matrix, entryRow, entryColumn):
        matrix[entryRow] = matrix[entryRow]/matrix[entryRow][entryColumn];
        i = 0;
        while i < len(matrix):
            if(i != entryRow):
                matrix[i] = matrix[i] - matrix[i][entryColumn]*matrix[entryRow]
            i += 1;
        return matrix;