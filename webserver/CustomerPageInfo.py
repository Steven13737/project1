def GetDict(a):
    #Create Seeion as dictionary
    name = []
    mid = []
    i=0
    while(i<len(a)):
        name.append(a[i])
        i=i+1
        mid.append(a[i])
        i=i+1
    namedict = dict(zip(name,mid))
    print namedict
    return namedict

#define a get result functions
def getresult(cursor):
    results = []
    for result in cursor:
        for i in range(len(result)):
            results.append(result[i])  # can also be accessed using result[0]
    cursor.close()
    #print(results)
    return results

#Get the consumed restaurant and the restaurant needed to be commmented
def GetResuaurant(g, text, CID):
        cmd = "select r.name, d.time_num from DateConsume d, Restaurant r where d.CID = (:CID) and r.RID = d.RID "
        cursor = g.conn.execute(text(cmd),CID = CID[0]);
        restaurant = getresult(cursor);

        #Find the restaurant name need to be commented
        cmd = "with NeedtoC(CID,RID,time) as ( \
                select CID,RID,time_num from DateConsume where CID = (:CID)\
                except \
                select CID,RID,time_num from Comment where CID=(:CID))\
                select r.name,r.RID from NeedtoC N, Restaurant r where N.RID = r.RID "
        cursor = g.conn.execute(text(cmd),CID = CID[0]);
        crestaurant = getresult(cursor);
        print crestaurant

        #Find the restaurant time need to be commented
        cmd = "with NeedtoC(CID,RID,time) as ( \
                select CID,RID,time_num from DateConsume where CID = (:CID)\
                except \
                select CID,RID,time_num from Comment where CID=(:CID))\
                select N.time from NeedtoC N, Restaurant r where N.RID = r.RID "
        cursor = g.conn.execute(text(cmd),CID = CID[0]);
        crestaurant_time = getresult(cursor);
        return restaurant, crestaurant, crestaurant_time

def VoteRestaurant(g, text, CID):
    cmd = "with voterestaurant(CID,RID) as (\
            select CID,RID from DateConsume where CID =  (:CID)\
            and RID not in(\
            select RID from Vote where CID =  (:CID)))\
            select r.Name from voterestaurant v, Restaurant r where v.RID = r.RID"
    cursor = g.conn.execute(text(cmd),CID = CID[0]);
    VoteRestaurantName = getresult(cursor);
    print VoteRestaurantName

    #Get Name and RID
    cmd = "with voterestaurant(CID,RID) as (\
            select CID,RID from DateConsume where CID =  (:CID)\
            except\
            select to_char(CID,'9999'),RID from Vote where CID =  (:CID))\
            select r.Name,r.RID from voterestaurant v, Restaurant r where v.RID = r.RID"
    cursor = g.conn.execute(text(cmd),CID = CID[0]);
    VoteRestaurantName_RID = getresult(cursor);

    return VoteRestaurantName,VoteRestaurantName_RID

def GetCID(g,text,username):
    #print username
    cmd = "select CID from Customer where email = (:username)"
    cursor = g.conn.execute(text(cmd),username = username);
    CID = getresult(cursor);
    #print CID
    return CID

def GetCuisineType(g,text):
    cmd = 'SELECT distinct Cuisine_Type FROM CuisineType'
    cursor = g.conn.execute(text(cmd));
    cui = []
    for result in cursor:
        cui.append(result[0])
    cursor.close()
    #print cui
    return cui
