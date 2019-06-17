#TODO
#coverage table
#change doc strings 
#add GUI and terminal interfaces
import sys
from colorclass import Color, Windows

from terminaltables import AsciiTable

class QM:
    def __init__(self,minterms,dcares=[], chars = []):


        #holds the procedure leading up to the solution
        self.procedure = ""

        #ensure that elements in minterms and dont_cares
        #are all integers
        minterms = [int(x) for x in minterms]


        if dcares:
            dcares = [int(x) for x in dcares]
    

        #get the number of bits to represent each binary
        #string. number of bits is the same as that needed
        # to represent the longest binary string 
        self.nbits = len(bin(max(minterms))[2:])
        
        #convert minterms and dont cares to binary
        self.minterms =  self.to_binary(minterms)
        
        if dcares:
            self.dont_cares = self.to_binary(dcares)

        else:
            self.dont_cares = []

        #holds all prime implicants based on dont cares and minterms
        self.prime_implicants = []

        #holds all minterms and dont cares that have combined
        self.combined = []

        #holds all essential prime implicants based on minterms
        #dont cares
        self.essential_prime_implicants = []

        #coverage table used in determining essential prime implicants
        self.coverage_table = {}

        #for example x,y,z  or a,b,c etc
        #wether or not to sort chars
        self.chars = sorted(chars)


    def to_binary(self,minterms=[],nbits = 0):
        """
        Converts every element in minterms to its binary representation.

        Args:
            minterms: A list of minterms.
            nbits: is the the number of bits to be used for the representation
                    if not specided the value defaults to the len of longest 
                    binary string in list 

        Returns:
            A list containing the binary represenation of each minterm in minterms
            Each binary string nbits long

        Example:
             if minterms[]
        """
        
        
        #get the max number of digits in any minterm
        if nbits:
            mx = nbits
        else:
            mx = self.nbits

        bminterms = [] #binary minterms
        for minterm in minterms:
            bstr = bin(minterm)[2:] 
            bstr = (mx - len(bstr))*'0'+bstr #append zeroes to the string 
            bminterms.append(bstr)

        return bminterms
   

    def combine(self,min1,min2):
        """
        Combines two minterms if they differ by exactly one position.

        Args:
            min1: Binary representation of of the first minterm.
            min2: Binary represenation of the second minterm.
            

        Returns:
            A new minterm with a dash in the position where the two minterms differ or
            None if they differ by more or less than one position

        """

        #get the positions where the two strings differ    
        pos = [i for i in range(len(min1)) if min1[i] != min2[i]]

        if len(pos) == 1:
            i = pos[0] #i is the index of the single difference position
            return min1[:i] + '_' + min1[i+1:]

    

    def combine_groups(self,group1=[],group2=[]):
        """
        Combines the in minterms in two groups of minterms.

        Args:
            group1: First group of minterms.
            group2: Second group of minterms.
            

        Returns:
            A dictionary {'combined': [], 'uncombined': []}
            uncombined are the minterms in the first group that failed to combine
            offspring are the results of the combination of the minterms in the first and second group

        """
        res = []


        #prime_implicants+=group1 + group2
        for mt1 in group1:
            has_combined = False #holds if the minterm has been able to combine atleast once
            for mt2 in group2:
                offspring = self.combine(mt1,mt2)
                
                if offspring:
                    has_combined = True

                    self.combined.append(mt1)
                    self.combined.append(mt2)

                    if offspring not in res:
                        res.append(offspring)
    
        return res


    def combine_generation(self,generation=[]):
        """
        Combines the groups in each generation.

        Args:
            generation:  A collection [] of groups to be combined
            

        Returns:
            A new generation [] of groups 

        """
        new_gen = []
    
        for i in range(len(generation)-1):
            new_group = self.combine_groups(generation[i],generation[i+1])
                    
            if new_group:
                new_gen.append(new_group)

        
        return new_gen

    def group_minterms(self,mts=[]):
        """
        Groups the elements in minterms according to the number of ones in their binary representation.

        Args:
            minterms: A non empty list of minterms in binary form.

        Returns:
            A dictionary of minterms where each key represents the number of ones present in the binary
            representation and each value is a list of minterms with an equal number of ones in their 
            binary representation
        Raises:
        """
        #sort  the minterms for presentation purpose
        mts.sort()
        grps = []
        num_groups = len(mts[0])


        ##########################for printing to the console##################################
        table_data = [
        [Color('{autogreen}Group{/autogreen}'),Color('{autogreen}Minterms (decimal){/autogreen}'), Color('{autogreen}Minterms (binary){/autogreen}')]
        ]
        table = AsciiTable(table_data)
        table.inner_row_border = True

        self.procedure+=Color('{autoblue}==========================\nStep 1 : Grouping Minterms\n==========================\n{/autoblue}\n')
        #########################################################################################

        for i in range(num_groups+1):
            grp = [x for x in mts if x.count('1')==i]

            if grp:
                grps.append(grp)

        ##################################for printing to the console###############################
                table_data.append([i,str(int(grp[0],2)),grp[0]])
                
                for j in range(1,len(grp)):
                    table.table_data[i][1]+="\n"+str(int(grp[j],2))
                    table.table_data[i][2]+="\n"+grp[j]
                    

        self.procedure+=str(table.table)
        ###########################################################################################

        
        return grps

    def pis(self):
        """
        Computes the prime implicants based on the minterms and dont cares

        Returns:
            A list containing the prime implicants 
        """
        mts = self.minterms + self.dont_cares
        new_gen = self.group_minterms(mts)
    
        #holds all the generations that are reached, used mainly for printing
        all_gens = [new_gen]
        
        while new_gen:
            for x in new_gen:
                for y in x:
                    self.prime_implicants.append(y)

            new_gen = self.combine_generation(new_gen)
            

            if new_gen:
                all_gens.append(new_gen)

        self.prime_implicants = [pi for pi in self.prime_implicants if pi not in self.combined]
        
        
        table_data = [
            []
        ]
        for gen in all_gens:
            i = all_gens.index(gen)

            table_data[0].append(Color('{autogreen} Stage '+str(i)+'{/autogreen}'))
            
            
        for gen in all_gens:
            i = all_gens.index(gen)
            for grp in gen:
                #only add rows for the first generation
                j = gen.index(grp)

                if i == 0:
                    temp = ["" for x in table_data[0]]
                    table_data.append(temp)

                for mt in grp:
                    table_data[j+1][i]+=str(mt)+"  "

                    if mt in self.combined:
                        table_data[j+1][i]+=u'\u2713'

                    else:
                        table_data[j+1][i]+='*'

                    table_data[j+1][i]+="\n"

        table = AsciiTable(table_data)
        table.inner_row_border = True

        self.procedure+=Color('\n\n{autoblue}===========================\nStep 2 : Combining Minterms\n===========================\n{/autoblue}\n')
        self.procedure+=table.table

    
        return self.prime_implicants
        
            
    def can_cover(self,pi,minterm):
        """
        Generates all possible permutations of the prime implicant

        Args:
            pi: A string representing the prime implicant

        Returns:
            A list containing all possible permutations of the prime implicant
        Raises:
        """
        #extract the minterm to also contain dashes where pi contains them 

        pos = [i for i in range(len(pi)) if pi[i]=='_']

        for i in range(len(pi)):
            if i not in pos and pi[i]!=minterm[i]:
                return False

        return True




    def primary_epis(self):
        """
        Computes the essential prime implicants based on the minterms and dont cares

        Returns:
            A list containing the essential prime implicants 
        """
        #for each minterm determine all the prime implicants that 
        #can cover it 
        for minterm in self.minterms:
            self.coverage_table[minterm] = []
            for pi in self.prime_implicants:
                #print(minterm,'   ',pi)
                if self.can_cover(pi,minterm):
                    self.coverage_table[minterm].append(pi)

        #find the prime implicants that are the only one covering any minterm
         #for printing the coverage table

        #################################################################################################
        table_data = [['']+[Color('{autogreen}'+str(int(x,2))+'{/autogreen}') for x in self.minterms]]

    
        for pi in self.prime_implicants:
            table_data.append([pi]+['' for x in self.minterms])

            for mt in self.minterms:
                if pi in self.coverage_table[mt]:
                    table_data[self.prime_implicants.index(pi)+1][self.minterms.index(mt)+1]='X'

                    if len(self.coverage_table[mt]) == 1:
                        table_data[self.prime_implicants.index(pi)+1][self.minterms.index(mt)+1]=Color('{autored}X{/autored}')

        table_data.append(['']+['' for x in self.minterms])
       
        #################################################################################################

        for minterm in self.minterms:
            if len(self.coverage_table[minterm]) == 1:
                self.essential_prime_implicants.append(self.coverage_table[minterm][0])
           
        #tick for the prime implicants that are covered
        for minterm in self.minterms:
            if set(self.coverage_table[minterm]).intersection(set(self.essential_prime_implicants)):
                table_data[-1][self.minterms.index(minterm)+1]=u'\u2713'

        #filter out any prime implicants that appear twice
        self.essential_prime_implicants = list(set(self.essential_prime_implicants))

       
        #reduce the coverage table to include only minterms not covered by the 
        #essential prime implicants

        self.coverage_table = {k:v for k,v in self.coverage_table.items() if \
            not set(v).intersection(set(self.essential_prime_implicants))}
      
        table = AsciiTable(table_data)
        table.inner_row_border = True

        self.procedure+=Color('\n\n{autoblue}=======================\nStep 3 : Coverage Chart\n=======================\n{/autoblue}\n')
        self.procedure+=table.table

        return self.essential_prime_implicants

    def secondary_epis(self):
        """
        Computes the secondary essential prime implicants

        Returns:
            A list containing the secondary essential prime implicants 
        """
        #adds the secondary essential prime implicants to the epis
        #returns the other non essential prime implicants necessary to  complete the coverage table
        #uses petricks method for computation
        pass


    def minimize(self,mterms=[],dcares=[],variables=[]):
        """
        Minimizes the circuit and returns the list of terms for minimized circuit

        Returns:
            A list containing both primary and secondary essential prime implicants 
        """

        if mterms:
            self.minterms = mterms
        
        if dcares:
            self.dont_cares = dcares

        if variables:
            self.chars = variables

        return self.primary_epis()+self.secondary_epis()

    def to_char(self,term,chars):
        """
        Converts the binary term to its character representation

        Args:
            term : A binary string representing the prime implicant

        Returns:
            A string with the character represenation fro the string
        """

        i = 0 
        res = ''
        for ch in term:
            if ch == '1':
                res+=chars[i]

            elif ch == '0':
                res=res+chars[i]+"'"

            i+=1

        return res



    