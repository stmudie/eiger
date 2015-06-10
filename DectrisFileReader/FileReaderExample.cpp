/*! 
 *  \brief     Example how to read entries from the NeXus header, and images
 *  \details  
 *  \author    Michael Rissi
 *  \author    Contact: support@dectris.com
 *  \version   0.1
 *  \date      21.11.2012
 *  \copyright See General Terms and Conditions (GTC) on http://www.dectris.com
 * 
 */



#include <iostream>

#include <vector>
#include <string>
#include "DNexusReadHelper.h"
#include <hdf5.h>
#include <map> 
using namespace DNexusReadHelper;
int main(int argc, char *argv[])
{
  if(argc != 3)
    {
      std::cout<<"usage: "<<argv[0]<<" <hdf5 master file> <[0,1]"<<std::endl;
      std::cout<<"0: Pilatus (32bit) data "<<std::endl;
      std::cout<<"1: Eiger (16bit) data "<<std::endl;
      return -1;
    }

  bool Eiger;
  if(atoi(argv[2]) == 0)
    Eiger = false;
  else
    Eiger = true;
  
  std::string masterFilename(argv[1]);
  
  /// open the file ///
  hid_t fid = H5Fopen(masterFilename.c_str(), H5F_ACC_RDONLY, H5P_DEFAULT);
  if(fid<0)
    {
      std::cout<<"cannot open file "<<masterFilename<<std::endl;
      exit(EXIT_FAILURE);
      
    }
  
  /// FIRST EXAMPLE: read an entry from the NeXus header ///
  
  
  /// open the detector group in /entry/instrument/detector : ///
  
  hid_t gid = H5Gopen2(fid, "/entry/instrument/detector/", H5P_DEFAULT);
  if(gid < 0)
    {
      std::cout<<"group /entry/instrument/detector/ does not exist"<<std::endl;
      exit(EXIT_FAILURE);
    }

 
  
  /// open the dataset count_time ///
  std::vector<float> count_time;
  std::vector<hsize_t> count_time_dim;
  std::string count_time_units;
  
  bool rc = ReadDatasetItem(gid, std::string("count_time"), &count_time, &count_time_dim, &count_time_units);
  if(!rc)
    {
      std::cout<<"cannot read dataset count_time"<<std::endl;
      exit(EXIT_FAILURE);
    }
  std::cout<<"value of count_time: "<<count_time[0]<<std::endl;
  std::cout<<"units: "<<count_time_units<<std::endl;


 
  
  /// read the detector description field as a string ///

  std::vector<std::string> description;
  std::vector<hsize_t> description_dim;
  std::string description_units;
  rc = ReadDatasetItem(gid, std::string("description"), &description, &description_dim, &description_units);
  std::cout<<description[0]<<std::endl;


  /// read some detector specific information ///
  hid_t gid_specific = H5Gopen2(gid, "detectorSpecific", H5P_DEFAULT);
  if(gid_specific<0)
    {
      std::cout<<"cannot open detector specific group"<<std::endl;
      exit(EXIT_FAILURE);
    }

  /// example of a 2D dataset: flatfield ///
  /// flatfield_dim will have two entries (dimx and dimy of the image) ///
  std::vector<float> flatfield;
  std::vector<hsize_t> flatfield_dim;
  std::string flatfield_units;
  rc = ReadDatasetItem(gid_specific, std::string("flatfield"), &flatfield, &flatfield_dim, &flatfield_units);
  if(!rc)
    {
      std::cout<<"cannot read dataset flatfield"<<std::endl;
      exit(EXIT_FAILURE);
    }





  /// detector photon energy //
  std::vector<float> photon_energy;
  std::vector<hsize_t> photon_energy_dim;
  std::string photon_energy_units;
  rc = ReadDatasetItem(gid_specific, std::string("photon_energy"), &photon_energy, &photon_energy_dim, &photon_energy_units);

  if(!rc)
    {
      std::cout<<"cannot read dataset photon_energy"<<std::endl;
      exit(EXIT_FAILURE);

    }

  std::cout<<"photon_energy: "<<photon_energy[0]<<" "<<photon_energy_units<<std::endl;



  /// read some module information ///
  hid_t mod_gid = H5Gopen2(gid_specific, "detectorModule_001", H5P_DEFAULT);
  if(mod_gid<0)
    {
      std::cout<<"cannot open module"<<std::endl;
      exit(EXIT_FAILURE);
    }
  


  H5Gclose(mod_gid);
  H5Gclose(gid_specific);
  H5Gclose(gid);

  
  ////////////////////////////
  ///                      ///
  /// example: read images ///
  ///                      ///
  ////////////////////////////

  /// first: create the look up table in order to be able to find image n:
  std::map<size_t, std::string> lut;
  std::cout<<"creating LUT..."<<std::endl;
  rc = CreateLUT(fid, &lut); 
  if(!rc)
    {
      std::cout<<"LUT creating failed."<<std::endl;
    }
  std::cout<<"LUT created"<<std::endl;
  int imageNr = 0;
  std::cout<<"read image nr: "<<imageNr<<std::endl;
  if(Eiger)
    {
      std::vector<uint16_t> img;
      std::vector<hsize_t> dim;
      dim.resize(2);
      // example: read image 101: ///

      
      rc = ReadImage(imageNr, lut, fid,  &img,  &dim);
      /// dimensions of this image are: ///
      std::cout<<"image dimensions: "<<dim[0]<<" "<<dim[1]<<std::endl;
      /// do some work with your image ///
      rc =DetermineProteinStructure(img, dim);



      /// or access the image pixel by pixel ///
      for(size_t pix_x = 0; pix_x <dim[0]; pix_x++)
	{
	  for(size_t pix_y = 0; pix_y <dim[1]; pix_y++)
	    {
	      uint16_t pxval = getPixelValue(pix_x, pix_y, img, dim);
	     
	    }
	}
     
      
    }
  else
    {
      std::vector<uint32_t> img;
      std::vector<hsize_t> dim;
      dim.resize(2);

      rc = ReadImage(imageNr, lut, fid,  &img,  &dim);
      std::cout<<"image dimensions: "<<dim[0]<<" "<<dim[1]<<std::endl;
      for(size_t pix_x = 0; pix_x <dim[0]; pix_x++)
	{
	  for(size_t pix_y = 0; pix_y <dim[1]; pix_y++)
	    {
	      uint32_t pxval = getPixelValue(pix_x, pix_y, img, dim);

	    }
	}
     

    }


  H5Fclose(fid);
}
