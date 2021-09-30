def fbx_merge():
    # get the fbx path #
    select_node = hou.selectedNodes()
    child = select_node[0].children()
    path = ""

    # get any geo node and copy the path #
    for x in child:
        if x.type().name() == "geo":
            path = x.children()[0].parm("file").eval()
            break

    # remove unwanted elements from path #
    end_part = path.split("/").pop(-1)
    front_part = "/".join(path.split("/")[:-1])
    fbx_path = front_part +"/"+ end_part.split("#")[:-1][0]

    # fetch the full fbx model and create necessary nodes #
    obj = hou.node("/obj")
    fbx = obj.createNode("geo", "fbx_import")
    fbx.moveToGoodPosition()
    filesop = fbx.createNode("file")
    matsop = fbx.createNode("matnet")
    matsop.moveToGoodPosition()
    material_sop = fbx.createNode("material", "materials1")
    material_sop.setInput(0, filesop)
    material_sop.moveToGoodPosition()
    filesop.parm("file").set(fbx_path)

    # get the materials #
    for count, i in enumerate(child):
        if i.name() == "materials":
            mats = i.children()
            hou.copyNodesToClipboard(mats)
            hou.pasteNodesFromClipboard(matsop)
        else:
            # get the materials for mats applied on geo nodes #
            mat_parm = i.parm("shop_materialpath").eval()

            # get the group name from file sop #
            geoChild0 = i.children()
            groupName = ""
            for y in geoChild0:
                if y.type().name() == "file":
                    groupName = y.parm("file").eval().split("/")[-1].split("#")[-1].split(",")[0]

            # set the materials on the new material nodes #
            if len(mat_parm) > 0 :
                globalCounter0 = material_sop.parm("num_materials").eval() + 1
                material_sop.parm("num_materials").set(globalCounter0)
                group = "group"+str(globalCounter0)
                matPath = "shop_materialpath"+str(globalCounter0)
                material_sop.parm(group).set("@name={}".format(groupName))

                # get the material path and change it according to new nodes #
                mat_path_list = i.parm("shop_materialpath").eval().split("/")
                del mat_path_list[0]
                mat_path_list[1] = fbx.name()
                mat_path_list[2] = "matnet1"
                mat_path = "/"+"/".join(mat_path_list)
                material_sop.parm(matPath).set(mat_path)

            # set the materials for mats applied using material sop #
            else:
                geoChild = i.children()
                mat_path = ""
                for j in geoChild:
                    # check for partition nodes and add one #
                    if j.type().name() == "partition":
                        fbxChildren = [x.type().name() for x in fbx.children()]

                        # create partition node only if it doesn't exist #
                        if "partition" not in fbxChildren:
                            partitionNode = fbx.createNode("partition")
                            partitionNode.parm("rule").set(j.parm("rule").unexpandedString())
                            partitionNode.setInput(0, fbx.children()[-2])

                    # gather all materials and groups in two lists #
                    elif j.type().name() == "material":
                        mat_list = []
                        group_list = []

                        # create final material node only if it doesn't exist #
                        if fbx.children()[-1].type().name() != "material":
                            FinalMat = fbx.createNode("material", "FinalMat")
                            FinalMat.setInput(0, fbx.children()[-2])

                        # check all parameters and only process group and material parms #
                        allParms = j.parms()
                        for parm in allParms:
                            if "shop_materialpath" in parm.name():
                                mat_path_list = parm.eval().split("/")
                                del mat_path_list[0]
                                mat_path_list[1] = fbx.name()
                                mat_path_list[2] = "matnet1"
                                mat_path = "/"+"/".join(mat_path_list)
                                mat_list.append(mat_path)
                            elif "group" in parm.name():
                                group_list.append(parm.eval())

                        # finally apply the proper groups and paths in out material node #
                        for count, mat in enumerate(mat_list):
                            currMatCount = FinalMat.parm("num_materials").eval()
                            globalCounter = currMatCount+1 # keeps addnig 1 in every loop to increase material slots #
                            FinalMat.parm("num_materials").set(globalCounter)
                            FinalMat.parm("group{}".format(globalCounter)).set(group_list[count])
                            FinalMat.parm("shop_materialpath{}".format(globalCounter)).set(mat_list[count])

    # add a final null and layout everything #
    null = fbx.createNode("null", "OUT")
    null.setInput(0, fbx.children()[-2])
    null.setGenericFlag(hou.nodeFlag.Display, 1)
    null.setGenericFlag(hou.nodeFlag.Render, 1)
    null.setGenericFlag(hou.nodeFlag.Template, 1)
    fbx.layoutChildren()



# run the function #
fbx_merge()
