

import re
import os
import json
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize


with open('C:/Users/Raghu/Desktop/Sparkshik/ADANI_BILL/output/output2/rstuv67747.json') as f:
    d = json.load(f)

x=d['lines']
y=d['join_lines']

dup=x
rem=re.findall(r'[-:\b\.wW]{1,10}',y,re.I)

for i in range(len(rem)):
	if rem[i] in dup:
		dup.remove(rem[i])

x=dup
y=" ".join(x)


main={
    'Address Block'   :       {},
    'Account Details' :       {},
    'Bill Amount'     :       None,
    'Bill Details'    :       {},
    'Previous Consumption' :  {}
    }

for i, item in enumerate(x):
    try:
        #---Account Details---#
        if re.search('ACCOUNT NO', item):
            ACC=i
            acc_no=x[ACC+1]
            total_nums=0
            for digits in acc_no:
                if digits.isdigit():
                        total_nums+=1
            if total_nums >=8:
                    main['Account Details']['ACCOUNT NO.']=x[ACC+1]
                    
            #print("Account No. : ",x[ACC+1])

        elif re.search('[A-Z][A-Z]LL [A-Z]O[A-Z]TH', item):
            MON=i
            bill_month=x[MON+1]
            month_char=0
            month_digit=0
            for counting in bill_month:
                    if counting.isalpha():
                            month_char+=1
                    elif counting.isdigit():
                            month_digit+=1
                    else:
                            pass
            
            if ((2<=month_char<=4) and (2<=month_digit<=4)):
                    for remove in bill_month:
                            if (remove.isdigit() or remove.isalpha()):
                                pass
                            else:
                                bill_month=bill_month.replace(remove,"-")
                    main['Account Details']['BILL MONTH']=bill_month
                    #print("Bill Month : ",x[MON+1])
        
        elif re.search('DUE DATE', item):
            DD=i
            countt=0
            for mynum in range(len(x[DD+1])):
                if x[DD+1][mynum].isdigit():
                    countt=countt+1
            
            if countt>=7:
                    if not x[DD+1][-1].isdigit():
                        x[DD+1]=x[DD+1].replace(x[DD+1][-1],"")
                        main['Account Details']['DUE DATE']=x[DD+1]
            else:
                countt=0
                try_due_date=x[DD+2]
                for mynum in range(len(x[DD+2])):
                    if x[DD+2][mynum].isdigit():
                        countt=countt+1
                if countt>=6:
                    main['Account Details']['DUE DATE']=x[DD+2]
                else:
                    pass
            #print("Due Date : ",x[DD+1])
        
        elif re.search(r'smiles', y,re.IGNORECASE):
            e=re.search(r'smiles', y,re.IGNORECASE).end()
            se=y[e:]
            smiley=re.search(r"[0-9]{1,4}", se).group()
            main['Account Details']['SMILEY EARNED']=smiley
        #---Account Details---#

        #elif re.search(r'Bill No',y,re.I):
            
        
        unwanted=None
        if re.search(r'RESIDENT|RESIDENTIAL|COMMERCIAL', item):
            NAME=i
            mat=re.match(r'[w]{0,10}',x[NAME+1],re.IGNORECASE)
            if mat.group():
                main['Address Block']['OWNER']=x[NAME+2]
            else:
                if bool(re.findall(r'bill|of|supply',x[NAME+1],re.I)) is True:
                    main['Address Block']['OWNER']=x[NAME+2]
                else: 
                    main['Address Block']['OWNER']=x[NAME+1]
                    mat2=re.match(r'[w]{0,10}',x[NAME+2],re.IGNORECASE)
                    if mat2.group():
                        unwanted=x[NAME+2]
                    else:
                        pass

        if re.search('DUE AMOUNT', item):
            AMOUNT=i
            amt=x[AMOUNT+1]
            amt=amt.strip()
            non_decimal = re.compile(r'[^\d.]+')
            amt=non_decimal.sub('',amt)

            main["Bill Amount"]=amt
            #print("Due Amount : ",x[AMOUNT+1])

        r=re.search(r'RESIDENTIAL|COMMERCIAL', y).end()
        add=y[r:]
        s=re.search(r"\b[0-9]{6}\b", add)
        
        if s is not None:
            s=re.search(r"\b[0-9]{6}\b", add).end()
        else:
            s=re.search(r"MUMBAI",add,re.I).end()
        
        add=add[:s]
        
        if unwanted is None:
    
            address=add.split((main['Address Block']['OWNER']))
            main['Address Block']["ADDRESS"]=address[len(address)-1].strip()
    
        else:
            address=add.split(unwanted)
            main['Address Block']["ADDRESS"]=address[len(address)-1].strip()
            
        pin=re.search(r"\b[0-9]{6}\b", add)
        if pin is not None:
            main['Address Block']['PIN CODE']=pin.group(0)
    
        
    except Exception:
        pass

try:
    bill_end=re.search(r'Bill No',y,re.I).end()
    bill_num=y[bill_end:]
    bill_number = re.findall(r'[0-9]{12}',bill_num)
    main['Bill Details']['Bill No']=bill_number[0]

    pin=re.search(r"\b[0-9]{6}\b", y)
    if pin is not None:
        main['Address Block']['PIN CODE']=pin.group(0)
        
except Exception:
        pass

try:
    non_digit=0
    a=re.search('mobile',y,re.I).end()
    i=y[a:a+25]
    
    for j in i:
        if j.isdigit():
            continue
        else:
            i=i.replace(j,"")
    number=re.search(r"[0-9]{10,12}",i).group()
    if len(number)==10:
        main['Address Block']['PHONE']=number
    else:
        main['Address Block']['PHONE']=number[:10]
    
except Exception:
    pass    


try:

    main_load=re.search(r'\b[a-z][a-z]nnected [a-z][a-z][a-z][a-z] in kw\b',y,re.I)
    if main_load is not None:
        main_load_end=main_load.end()
        main_load_end=y[main_load_end:]
        main_load_in_kw=re.findall(r"([\d.]*\d+)", main_load_end)
        main['Address Block']['CONNECTED LOAD']=main_load_in_kw[0]
    else:
        load=re.search(r'[a-z]?[a-z]?nnected [l|c][a-z][a-z][a-z]',y,re.IGNORECASE).end()
        temp_load=y[load:]
        load2=re.search(r'[a-z:]?w',temp_load,re.IGNORECASE).end()
        load3=(y[load:load+load2]).strip()
    
        for i in load3:
            if i.isalpha():
                pass
            elif i.isdigit():
                pass
            else:
                load3=load3.replace(i,".")
   
        load3=load3[:-2] + " kW"
        if load3[0].isdigit() and not load3[1].isdigit():
            main['Address Block']['CONNECTED LOAD']=load3
        elif load3[0].isdigit() and load3[1].isdigit():
            load3=load3[0] + "." + load3[1:]
            main['Address Block']['CONNECTED LOAD']=load3
        
except Exception:
    pass

dic_update={}
clearing=["jan","feb","mar","apr","may","jun","jul","aug","sep","oct","nov","dec"]
for key in clearing:
    dic_update[key]=None

for i,item in enumerate(x):
    try:
        cons=re.findall(r'(?:[a-z][a-z]n|Feb|Mar|[a-z][a-z][a-z]|May|Ju[1,n,l]|Ju[a-z]|Aug|S[a-z][a-z]|O[a-z][a-z]|No[a-z]|D[a-z][a-z])[ ]?[-:\. ]?[ ]?[0-9]{2,3}',item,re.I)
        if cons:
            val=x[i+1]
            
            if val.isdigit():
                string = ''.join(cons)        #returns the normal string
               
                alpha=0
                digit=0
                for l in string:
                    if l.isalpha():
                        alpha=alpha+1
                    elif l.isdigit():
                        digit=digit+1
                    else:
                         pass
                        
                month=string[:alpha].lower()
                month=month[0].upper() + month[1:]
                
                string=month+"-"+string[-2:]
                string=string.strip()

                if (month.lower() in dic_update) and (dic_update[month.lower()]==None) :
                    dic_update[month.lower()]=1
                    main['Previous Consumption'][string]=x[i+1]
   
                else:
                    if (month.lower().startswith('de')) or (month.lower().endswith('ec')) or ((month.lower().startswith('d')) and month.lower().endswith('c')):
                        string="Dec"+"-"+string[-2:]
                        main['Previous Consumption'][string]=x[i+1]
                        dic_update[string.lower()[:3]]=1
                    
                    elif (month.lower().startswith('no')) or (month.lower().endswith('ov')) or ((month.lower().startswith('n')) and month.lower().endswith('v')):
                        string="Nov"+"-"+string[-2:]
                        main['Previous Consumption'][string]=x[i+1]
                        dic_update[string.lower()[:3]]=1
                
                    elif (month.lower().startswith('oc')) or (month.lower().endswith('ct')) or ((month.lower().startswith('o')) and month.lower().endswith('t')):
                        string="Oct"+"-"+string[-2:]
                        main['Previous Consumption'][string]=x[i+1]
                        dic_update[string.lower()[:3]]=1

                    elif (month.lower().startswith('se')) or (month.lower().endswith('ep')) or ((month.lower().startswith('s')) and month.lower().endswith('p')):
                        string="Sep"+"-"+string[-2:]
                        main['Previous Consumption'][string]=x[i+1]
                        dic_update[string.lower()[:3]]=1
                    
                    elif (month.lower().startswith('au')) or (month.lower().endswith('ug')) or ((month.lower().startswith('a')) and month.lower().endswith('g')):
                        string="Aug"+"-"+string[-2:]
                        main['Previous Consumption'][string]=x[i+1]
                        dic_update[string.lower()[:3]]=1

                    elif (month.lower().startswith('ma')) or (month.lower().endswith('ay')) or ((month.lower().startswith('m')) and month.lower().endswith('y')):
                        string="May"+"-"+string[-2:]
                        main['Previous Consumption'][string]=x[i+1]
                        dic_update[string.lower()[:3]]=1
                        
                    elif (month.lower().startswith('ap')) or (month.lower().endswith('pr')) or ((month.lower().startswith('a')) and month.lower().endswith('r')):
                        string="Apr"+"-"+string[-2:]
                        main['Previous Consumption'][string]=x[i+1]
                        dic_update[string.lower()[:3]]=1
                    
                    elif (month.lower().startswith('fe')) or (month.lower().endswith('eb')) or ((month.lower().startswith('f')) and month.lower().endswith('b')):
                        string="Feb"+"-"+string[-2:]
                        main['Previous Consumption'][string]=x[i+1]
                        dic_update[string.lower()[:3]]=1
                        
                    elif (month.lower().startswith('ja')) or (month.lower().endswith('an')) or ((month.lower().startswith('j')) and month.lower().endswith('n')):

                        string="Jan"+"-"+string[-2:]
                        main['Previous Consumption'][string]=x[i+1]
                        dic_update[string.lower()[:3]]=1

                    elif (month.lower().startswith('ma')) or (month.lower().endswith('ar')) or ((month.lower().startswith('m')) and month.lower().endswith('r')):
                        string="Mar"+"-"+string[-2:]
                        main['Previous Consumption'][string]=x[i+1]
                        dic_update[string.lower()[:3]]=1

                    elif (month.lower().endswith('un')):
                        string="Jun"+"-"+string[-2:]
                        main['Previous Consumption'][string]=x[i+1]
                        dic_update[string.lower()[:3]]=1

                    elif (month.lower().endswith('ul')) or ((month.lower().startswith('j')) and (month.lower().endswith('l'))):
                        string="Jul"+"-"+string[-2:]
                        main['Previous Consumption'][string]=x[i+1]
                        dic_update[string.lower()[:3]]=1

                    elif (month.lower().startswith('ju')):
                        jun=dic_update.get('jun')
                        jul=dic_update.get('jul')
                        if jul is None:
                            string="Jul"+"-"+string[-2:]
                            main['Previous Consumption'][string]=x[i+1]
                            dic_update[string.lower()[:3]]=1
                        elif jun is None:
                            string="Jun"+"-"+string[-2:]
                            main['Previous Consumption'][string]=x[i+1]
                            dic_update[string.lower()[:3]]=1
                        else:
                            pass

                    
                    #print("Updated Last : ",dic_update)
               
    except Exception:
        pass

#print(dic_update)

#email = re.search(r'[\w\.-b]+@[\w\.-]+(\.[\w]+)+',y)
#if email is not None:
#    email=email.group(0)
#    main['Address Block']['EMAIL ID']=email

try:
        main['Account Details']['ACCOUNT NO.']
except KeyError:
        if re.search(r'\b[0-9]{9}\b',y) is not None:
                main['Account Details']['ACCOUNT NO.']=re.search(r'\b[0-9]{9}\b',y).group(0)        
        try:
                main['Account Details']['BILL MONTH']
        except KeyError:
                if re.search(r'\b(JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)\-[0-9]{2}\b',y) is not None:
                        mo=re.search(r'\b(JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)\-[0-9]{2}\b',y)
                        main['Account Details']['BILL MONTH']=mo.group(0)   
print(main)

with open('C:/Users/Raghu/Desktop/Sparkshik/ADANI_BILL/JsonOutput/info.json', 'w') as f:
    json.dump(main, f)
