# --------------------------------------------------------------------------- #

from maya import cmds, mel
import maya.api.OpenMaya as om

# --------------------------------------------------------------------------- #

ZOOM_TRANSLATE   = 'zoom_translate'
CAMERA           = []
SELECTED_OBJECTS = []
MOVE_DATA        = {}
MOUSE_START      = []
MOUSE_SCALE      = 1.0


# --------------------------------------------------------------------------- #

def zoom_translate():
    if cmds.contextInfo(ZOOM_TRANSLATE, exists=True):
        cmds.setToolTo(ZOOM_TRANSLATE)
        return

    cmds.draggerContext( ZOOM_TRANSLATE
                       , pressCommand   = 'start_translate()'
                       , dragCommand    = 'do_translate()'
                       , releaseCommand = 'end_translate()'
                       , cursor = 'hand'
                       , undoMode='step')
    
    # Put it as the y-key slot
    mel.eval('$gNonSacredTool = "{}";'.format(ZOOM_TRANSLATE))
    cmds.setToolTo(ZOOM_TRANSLATE)
    
    
def start_translate():    
    global CAMERA
    global MOVE_DATA
    global MOUSE_START
    
    if cmds.draggerContext(ZOOM_TRANSLATE, q=True, bu=True) == 1:
        cmds.setToolTo('selectSuperContext')
        cmds.warning('Use the middle mouse button to slide objects toward/away from camera')
        return

    sel = cmds.ls(sl=1, fl=1)
    # Probably should eventually put some logic here to validate the selection
    if len(sel) == 0:
        cmds.setToolTo('selectSuperContext')
        print 'Nothing selected'
        return
    
    active_panel = cmds.getPanel(wf=True)
    CAMERA = cmds.modelPanel(active_panel, q=True, cam=True)
    CAMERA = CAMERA.replace('Shape', '')
    
    target_loc = cmds.xform(CAMERA, q=True, ws=True, a=True, rp=True)
    destination_vec = om.MVector(target_loc)
    MOUSE_START = cmds.draggerContext(ZOOM_TRANSLATE, q=True, ap=True)
    
    for each in sel:
        loc = cmds.xform(each, q=True, ws=True, a=True, rp=True)
        vec = om.MVector(loc)
        diff_vec = vec - destination_vec
        MOVE_DATA[each] = [vec, diff_vec]


def do_translate():
    mouse_pos = cmds.draggerContext(ZOOM_TRANSLATE, q=True, dp=True)
    mouse_pos = MOUSE_START[0] - mouse_pos[0]

    manip_scale = MOUSE_SCALE * 0.0025
    manip_amount = mouse_pos * manip_scale
    
    for each in MOVE_DATA.keys():
        vec_scale = MOVE_DATA[each][1] * manip_amount
        vec_manip = MOVE_DATA[each][0] + vec_scale
        cmds.xform(each, ws=True, t=vec_manip)

    cmds.refresh()


def end_translate():
    global MOVE_DATA
    MOVE_DATA = {}
