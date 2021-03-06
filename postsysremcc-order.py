import numpy as np
from ultramodule import divstd_prime, crossco, cc_multiorde
import h5py
from  tqdm import tqdm
from tqdm import tnrange
from PyAstronomy import pyasl
###################################################################################################                                                                            
specdir="./rainbow/"
opt_tech="-fin"
len_sys=10
vmr_min=8
vmr_max=11
whichdata="kawa"
mol="tio"


###################################################################################################                                                              
from scipy import stats
def rankmat(mat):
    temp = mat.argsort()
    rank = temp.argsort()
    return rank
def cc_sp(mat1,mat2):
    r1=rankmat(mat1)
    r2=rankmat(mat2)
    sp1=r1-np.mean(r1)
    sp2=r2-np.mean(r2)
    up=np.sum(sp1*sp2)
    below=np.sqrt(np.sum(sp1*sp1)*np.sum(sp2*sp2))
    cc=up/below
    return cc              


ccd_list_2breduced=["blue","red"]
h5f_techni = h5py.File("techni-"+str(whichdata)+str(opt_tech)+".info", 'r')
drvs=h5f_techni["Doppler shifts variation"][:]
template="rainbow-wasp33kawaall_tio_template-shuff-fin.h5"
h5f_temp = h5py.File(specdir+"template/"+template, 'r')
h5f_reduced = h5py.File(specdir+"post_sysrem/rainbow"+str(whichdata)+"_postsysrem-superorder.h5", 'r')
for ccd in ccd_list_2breduced:
    if ccd=="blue":
        len_order=19
    else:
        if whichdata=="este":
            len_order=16
        else:
            len_order=13
    output_cc=str(ccd)+"-wasp33"+str(whichdata)+"_"+str(mol)+"shuff_cc_pearson-"+str(opt_tech)+"-superorder-hp.h5" 
    print output_cc
    h5f_cc = h5py.File(specdir+"post_sysrem/cc_result/"+str(output_cc), 'w')
    for vmr in tqdm(range(vmr_min,vmr_max),ascii="True",desc="VMR"):
        cc_map_full=[]
        for systematics in tqdm(range(len_sys),ascii="True",desc="Nsys"):
            cc_svd_collect=[] #Different SV are saved in this matrix
            for order in tqdm (range(1,len_order),ascii="True",desc="Order"):
                y_temp_order=h5f_temp[str(ccd)+"-vmr-"+str(vmr)+"-order-"+str(order)][:]
                yobs=h5f_reduced[str(ccd)+"-flux-order-"+str(order)+"sysrem"][:][systematics]
                for filenum in range (len(yobs)):
                    sm = pyasl.smooth(yobs[filenum], 25, 'flat')
                    sm1 = pyasl.smooth(sm, 51, 'flat')
                    yobs[filenum]=(yobs[filenum]+1.)/(sm1+1.)-1.
                std_frames=[]
                std_pix=[]
                for wvbin in range (len(yobs[1])):
                    std_pix.append(np.std(yobs[:,wvbin]))
                for filenum in range (len(yobs)):
                    std_frames.append(np.std(yobs[filenum,:]))
                std_frames=np.array(std_frames,dtype="float")
                yobs=divstd_prime(yobs,std_pix,std_frames)
                cc_order=np.zeros((len(yobs),len(drvs)),dtype="float")
                for numspec in range(len(yobs)):
                    for rv in range(len(drvs)):
                        cc_order[numspec][rv]=crossco(yobs[numspec],y_temp_order[rv])
                cc_svd_collect.append(cc_order)
            cc_map_full.append(cc_svd_collect)
        h5f_cc.create_dataset(str(ccd)+"_cc_vmr_"+str(vmr), data=cc_map_full)#Writing the template of the specific vmr
    h5f_cc.close()
h5f_reduced.close()
