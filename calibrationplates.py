import adsk.core, adsk.fusion, adsk.cam, traceback
from random import random

def extrude(sketchText,extrudes,distance = 0.1):
    extInput = extrudes.createInput(sketchText, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    distance = adsk.core.ValueInput.createByReal(distance)
    extInput.setDistanceExtent(False, distance)
    extInput.isSolid = True
    return extInput

def create_multiline_sketch_text(sketchTexts, textinput, textsize, xmin, ymin, xmax, ymax, horizontalAlignment, verticalAlignment):
    sketchText_var = sketchTexts.createInput2(textinput, textsize)
    sketchText_var.textStyle = adsk.fusion.TextStyles.TextStyleBold
    
    cornerPoint = adsk.core.Point3D.create(xmin, ymin, 0)
    diagonalPoint = adsk.core.Point3D.create(xmax, ymax, 0)
    characterSpacing = 0
    
    sketchText_var.setAsMultiLine(cornerPoint, diagonalPoint, horizontalAlignment, verticalAlignment, characterSpacing)
    
    return sketchTexts.add(sketchText_var)  # return the created sketchText object

def format_number(num):
    if round(num,1)%1==0:
        return str(int(num))
    else:
        return "{:.1f}".format(num)

def removeZero(sepdigits):
    return f"{(sepdigits):.2f}".replace("-0","-").lstrip("0") #remove zero

def extrudefunc(sketch,dist,cut,extrudes):
    if cut:
        extrudeInput = extrudes.createInput(sketch, adsk.fusion.FeatureOperations.CutFeatureOperation)
        extent_distance = adsk.fusion.DistanceExtentDefinition.create(adsk.core.ValueInput.createByString(f"{dist:.2f}cm"))
        extrudeInput.setOneSideExtent(extent_distance,adsk.fusion.ExtentDirections.NegativeExtentDirection)

    else:
        extrudeInput = extrudes.createInput(sketch, adsk.fusion.FeatureOperations.JoinFeatureOperation)
        extent_distance = adsk.fusion.DistanceExtentDefinition.create(adsk.core.ValueInput.createByString(f"{dist:.2f}cm"))
        extrudeInput.setOneSideExtent(extent_distance,adsk.fusion.ExtentDirections.PositiveExtentDirection)

    return extrudes.add(extrudeInput)

fusion = None
def run( context ):
    try:
        #-- Fusion360 Application Instance
        #--
        global fusion
        fusion = adsk.core.Application.get( )
        design = adsk.fusion.Design.cast( fusion.activeProduct )
        objColl = adsk.core.ObjectCollection.create()
        components = design.rootComponent.occurrences
        component = components.addNewComponent( adsk.core.Matrix3D.create( ) ).component
        extrudes = component.features.extrudeFeatures # outward extrudes (text etc)
        sketch1 = component.sketches.add( component.xYConstructionPlane )
        # Get the SketchCircles collection from an existing sketch.
        
        mm = 0.1
        ################################
        #x Increments
        start = 1*mm
        stop = 10*mm
        xincrement = 1.*mm

        #Y-increments
        yincrement_start = 0.0*mm
        yincrement_stop = 1.*mm
        yincrement = 0.1*mm

        #Parameters
        cutpoles = True
        cuttext = False
        textsize = 7*mm
        textthickness = 0.5*mm
        box_thickness = 5*mm
        separationx = 5*mm
        separationy = 2*mm
        maxheight = 10*mm
        xdimneg = -15*mm
        ydimneg = -2*mm

        #######################################

        xpos = 0
        ypos = 0
        ypos_last=0
        
        yincrements = int((yincrement_stop-yincrement_start)/yincrement)
        xincrements = int((stop-start)/xincrement)

        sketch2 = component.sketches.add( component.xYConstructionPlane )
        circles = sketch2.sketchCurves.sketchCircles
        
        sketch_text = component.sketches.add( component.xYConstructionPlane )
        ## Get sketch texts 
        sketchTexts = sketch_text.sketchTexts        
        # Create sketch text input

        
        ypos = textsize+stop/2+separationy
        xpos = stop/2+separationx
        num_circles = 0
        firstrun = True

        for xinc in range(0,xincrements+1):
            size = start+ xincrement*xinc

            for inc in range(0,yincrements+1):
                circlesize = size+inc*yincrement+yincrement_start
                if circlesize < maxheight:
                    extrudeheight = circlesize
                else:
                    extrudeheight = maxheight
                num_circles+=1
                ypos_last=ypos

                if stop+separationy > textsize+separationy:
                    ypos += stop+separationy
                else:
                    ypos += textsize+separationy
            xpos += size+separationx
            ypos = textsize+stop/2+separationy
        xpos -= size+separationx


        sketch1 = component.sketches.add( component.xYConstructionPlane )
        # Get the SketchLines collection from an existing sketch.S
        lines = sketch1.sketchCurves.sketchLines
        # Call an add method on the collection to create a new line.
        axis = lines.addTwoPointRectangle(adsk.core.Point3D.create(xdimneg,ydimneg,0), adsk.core.Point3D.create(xpos+size/2+textsize,ypos_last+size/2+textsize,0))
        ext = extrudes.add(extrude(sketch1.profiles.item(0),extrudes,-box_thickness))
        # Create the extrusion
        

        ypos = textsize+stop/2+separationy
        xpos = stop/2+separationx
        num_circles = 0
        firstrun = True

        for xinc in range(0,xincrements+1):
            size = start+ xincrement*xinc

            for inc in range(0,yincrements+1):
                circlesize = size+inc*yincrement+yincrement_start

                if firstrun:
                    sepdigits = (circlesize/mm)-int(circlesize/mm) # remove firist digit
                    textinput = removeZero(sepdigits)
                    xmin = -textsize
                    ymin = ypos-textsize/2
                    xmax = 0 
                    ymax = ypos+textsize/2
                    verticalAlignment = adsk.core.VerticalAlignments.TopVerticalAlignment
                    horizontalAlignment = adsk.core.HorizontalAlignments.RightHorizontalAlignment
                    sketchText = create_multiline_sketch_text(sketchTexts, textinput, textsize, xmin, ymin, xmax, ymax, horizontalAlignment, verticalAlignment)
                    ext = extrudefunc(sketchText,textthickness,cuttext,extrudes)
                
                circle1 = circles.addByCenterRadius(adsk.core.Point3D.create(xpos,ypos,0), (circlesize)/2)
                if circlesize < maxheight:
                    extrudeheight = circlesize
                else:
                    extrudeheight = maxheight
                
                if cutpoles:
                    dist = box_thickness+0.1
                else:
                    dist = extrudeheight
                ext = extrudefunc(sketch2.profiles.item(num_circles),box_thickness,cuttext,extrudes)

                num_circles+=1
                ypos_last=ypos

                if stop+separationy > textsize+separationy:
                    ypos += stop+separationy
                else:
                    ypos += textsize+separationy


            firstrun = False
            
            sketchText_var = sketchTexts.createInput2(format_number(size/mm), textsize)
            sketchText_var.textStyle = adsk.fusion.TextStyles.TextStyleBold
            
            cornerPoint = point = adsk.core.Point3D.create(xpos-textsize/2,-1*mm,0)
            diagonalPoint = point = adsk.core.Point3D.create(xpos+textsize/2,-1*mm+textsize,0)
            horizontalAlignment = adsk.core.HorizontalAlignments.CenterHorizontalAlignment
            verticalAlignment = adsk.core.VerticalAlignments.TopVerticalAlignment
            characterSpacing = 0
            
            sketchText_var.setAsMultiLine(  cornerPoint,
                                            diagonalPoint,
                                            horizontalAlignment,
                                            verticalAlignment,
                                            characterSpacing)
            #bbox = [sketchText_var.boundingBox.maxPoint,sketchText_var.boundingBox.minPoint]
            sketchText = sketchTexts.add(sketchText_var)

            ext = extrudefunc(sketchText,textthickness,cuttext,extrudes)
            
            xpos += size+separationx
            ypos = textsize+stop/2+separationy



    except:
        #-- Report Errors
        #--
        if( fusion ):
            fusion.userInterface.messageBox( traceback.format_exc( ) )