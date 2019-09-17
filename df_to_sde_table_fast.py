def edit_table(df, sde_table, fieldnames=None,
               enviro="C:/Users/paulinkenbrandt/AppData/Roaming/Esri/Desktop10.6/ArcCatalog/UGS_SDE.sde"):
    """
    this function will append rows to an existing SDE table from a pandas dataframe. It requires editing privledges.
    :param df: pandas dataframe with data you wish to append to SDE table
    :param fieldnames: names of fields you wish to import
    :param sde_table: name of sde table
    :param enviro: path to connection file of the SDE
    :return:
    """
    arcpy.env.workspace = enviro

    if len(fieldnames) > 0:
        pass
    else:
        fieldnames = df.columns

    read_descr = arcpy.Describe(sde_table)
    sde_field_names = []
    for field in read_descr.fields:
        sde_field_names.append(field.name)
    sde_field_names.remove('OBJECTID')

    for name in fieldnames:
        if name not in sde_field_names:
            fieldnames.remove(name)
            print("{:} not in {:} fieldnames!".format(name, sde_table))

    try:
        egdb_conn = arcpy.ArcSDESQLExecute(enviro)
        egdb_conn.startTransaction()
        print("Transaction started...")
        # Perform the update
        try:
            # build the sql query to pull the maximum object id
            sqlid = """SELECT max(OBJECTID) FROM {:};""".format(sde_table)
            objid = egdb_conn.execute(sqlid)

            subset = df[fieldnames]
            rowlist = subset.values.tolist()
            # build the insert sql to append to the table
            # this creates the first part of the insert statement, listing the fields to insert
            sqlbeg = "INSERT INTO {:}({:},OBJECTID)\nVALUES ".format(sde_table, ",".join(map(str, fieldnames)))
            sqlendlist = []
            # this creates the lists of data to insert
            for j in range(len(rowlist)):
                objid += 1
                strfill = []
                # This loop deals with different data types and NULL values
                for k in range(len(rowlist[j])):
                    # if null replace python None with string NULL
                    if pd.isna(rowlist[j][k]):
                        strvar = "NULL"
                    elif rowlist[j][k]:
                        strvar = "NULL"
                    # if number, no commas in SQL
                    elif isinstance(rowlist[j][k], (int)):
                        strvar = "{:0.0f}".format(rowlist[j][k])
                    elif isinstance(rowlist[j][k], (float)):
                        strvar = "{:0.4f}".format(rowlist[j][k])
                    # if string, add commas around sql text
                    else:
                        strvar = "'{:}'".format(rowlist[j][k])
                    # put a parenthesis around the beginning of each list
                    if k == 0:
                        strvar = "(" + strvar
                    strfill.append(strvar)
                strfill.append(" {:})".format(objid))
                # join all list items into one long string with commas
                sqlendlist.append(",".join(map(str, strfill)))

            sqlend = "{:}".format(",".join(sqlendlist))
            sql = sqlbeg + sqlend
            #print(sql)
            egdb_return = egdb_conn.execute(sql)

            # If the update completed successfully, commit the changes.  If not, rollback.
            if egdb_return == True:
                egdb_conn.commitTransaction()
                print("Committed Transaction")
            else:
                egdb_conn.rollbackTransaction()
                print("Rolled back any changes.")
                print("++++++++++++++++++++++++++++++++++++++++\n")
        except Exception as err:
            print(err)
            egdb_return = False
        # Disconnect and exit
        del egdb_conn
    except Exception as err:
print(err)
