from django.http import HttpResponse
from django.shortcuts import render
import pandas as pd
import operator
from django.shortcuts import render
from django.http import HttpResponse
import pandas as pd
import boto3
import time
import uuid
from datetime import datetime
from decimal import Decimal
from dynamodb_json import json_util as json
from boto3.dynamodb.conditions import Key

def home(request):
    return render(request,'home.html')

def count1(request):
    fulltext=request.GET['fulltext']
    return render(request,'count.html',{'dict':fulltext})

    #return render(request,'count.html',{'fulltext':fulltext,'count':len(wordlist),'dict':sortedwords,'unique':len(wlst)})



def about(request):
    return render(request,'about.html')



dynamodb=boto3.resource('dynamodb',region_name='ap-south-1')
recipe=dynamodb.Table('Recipe')
js=json.loads(recipe.scan())
ingredients=dynamodb.Table('inventory')
js1=json.loads(ingredients.scan())


ingredientlist=[]
newdict={}
for item in js1['Items']:
    ingredientlist=ingredientlist+[{'item':item['item'],'Image':item.get('image'),'quantity':item.get('quantity'),'type':item.get('type')}]

#print(ingredientlist)



for names in ingredientlist:
    name=names.pop('item')
    newdict[name]=names

print("newdict",newdict)




def alldishes(mustuse):
    finalrecipes=[]    
    dishes={}
    have=set()
    for items in js['Items']:
            print(items.keys)
            dishes.update({items['Dish']:{'ingredients':set(items['Ingredients']),'recipe':items['Recipe'],'Image':items['Image'],'Region':items['Region'],"Time":items['Time'],"Type":items['Type'],"Link":items["Link"]}})
   

    for ingredient in js1['Items']:
        if ingredient['quantity']!=0:
            have.add(ingredient['item'])


    for dish in dishes:
        needed=dishes.get(dish).get('ingredients')
        diff=needed.difference(have)
        dish_ingredients=dishes.get(dish).get('ingredients')
        
        dish_ingredient_detail={}
        for dish_ingredient in dish_ingredients:
            dish_ingredient_detail[dish_ingredient]=newdict.get(dish_ingredient)
        

        already=dishes.get(dish).get('ingredients').intersection(have)
        dishtype=dishes.get(dish).get('Type')
        region=dishes.get(dish).get('Region')
        cooktime=dishes.get(dish).get('Time')
        Link=dishes.get(dish).get('Link')
        Image=dishes.get(dish).get('Image')
        dishresult=dish
        print('dishresult:',dishresult)

        if len(mustuse.intersection(needed))==len(mustuse):
            if len(already)!=0:
                if len(diff)==0:        
                    dishresult={'dish':dish,'needed':needed,'diff':diff,'already':already,'dishtype':dishtype,'region':region,'cooktime':cooktime,'Link':Link,'Status':'Have everything','Image':Image,'dish_ingredients':dish_ingredients,'dish_ingredient_detail':dish_ingredient_detail}
                else:
                    dishresult={'dish':dish,'needed':needed,'diff':diff,'already':already,'dishtype':dishtype,'region':region,'cooktime':cooktime,'Link':Link,'Status':('Need'+str(diff)),'Image':Image,'dish_ingredients':dish_ingredients,'dish_ingredient_detail':dish_ingredient_detail}
            else:
                dishresult={'dish':dish,'needed':needed,'diff':diff,'already':already,'dishtype':dishtype,'region':region,'cooktime':cooktime,'Link':Link,'Status':'Need everything','Image':Image,'dish_ingredients':dish_ingredients,'dish_ingredient_detail':dish_ingredient_detail}

            #print(reciperesponse)
            finalrecipes=finalrecipes+[dishresult]
                        
    return finalrecipes

def count(request):
    fulltext=set(request.GET['fulltext'].split(","))
    fulltext={i for i in fulltext if i}
    print(fulltext)
    reciperesp=alldishes(fulltext)
    return render(request,'count.html',{'response':reciperesp})

def ingredient(request):
    ingredients=[]
    for item in js1['Items']:
        ingredients=ingredients+[{'item':item['item'],'Image':item.get('image')}]
    #print("ingr",ingredients)
    return render(request,'form.html',{'ingredients':ingredients})
