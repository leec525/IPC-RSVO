//
// Created by xlab on 19-6-23.
//

#include <iostream>
#include <fstream>
#include <sstream>
#include <iomanip>
#include <math.h>
#include <random>
#include <algorithm>
#include <interpolation.h>
#include <opencv/cv.h>
#include <opencv/highgui.h>
#include <opencv2/imgcodecs.hpp>
#include <opencv/cv.hpp>
#include <boost/random.hpp>
#include <ctime>

using namespace alglib;

using namespace std;
using namespace cv;

struct MyRgb
{
    unsigned char red;
    unsigned char green;
    unsigned char blue;
};

string emorName = "../config/emor.txt";//config dir
string invemorName = "../config/invemor.txt";//config dir

spline1dinterpolant interpolateIrrgivenbri_r;
spline1dinterpolant interpolateIrrgivenbri_g;
spline1dinterpolant interpolateIrrgivenbri_b;

spline1dinterpolant interpolateBrigivenirr_r;
spline1dinterpolant interpolateBrigivenirr_g;
spline1dinterpolant interpolateBrigivenirr_b;

vector<double>emorE0;
vector<double>emorF0;
vector<double>emorB0;
vector<double>emorG0;

bool isLinearCRF = true;

float sigma_s;// = 0.04;
float sigma_c;// = 0.02;

float sigma_red_s;//   = sigma_s;
float sigma_green_s;// = sigma_s;
float sigma_blue_s;//  = sigma_s;
float sigma_red_c;//   = sigma_c;
float sigma_green_c;// = sigma_c;
float sigma_blue_c;//  = sigma_c;


void InitSigma();
void AddGaussianNoNoise(MyRgb& rgb);

void AddGaussianNoise(MyRgb& rgb,
                      float sigma_red_s,float sigma_red_c,
                      float sigma_green_s,float sigma_green_c,
                      float sigma_blue_s,float sigma_blue_c,
                      bool noise_flag, bool calc_irr_only);
void GetFileXY(vector<double> &xVector, vector<double> &yVector, string filename);//model xy coordinates.

spline1dinterpolant GetSpline1dinterpolant(vector<double> &xVector, vector<double> &yVector, bool isLinearCRF);

void GetParameter(string emorName,string invemorName);

void ImageAfterCRF(string strPathToSequence,
                   string distDir,
                   string imagePrefix,
                   bool addNoise,
                   string sigmas,
                   string sigmac);

int main(int argc, char **argv)
{
    if (argc != 6) {
        cout<<"parameter number error!"<<endl;
        return 1;
    }
    GetParameter(emorName, invemorName);
    bool addNoise = true;
    string strPathToSequenceSrc = argv[1];
    string strPathToSequenceDist = argv[2];
    string imagePrefix = argv[3];
    sigma_s = atof(argv[4]);
    sigma_c = atof(argv[5]);
    InitSigma();
    ImageAfterCRF(strPathToSequenceSrc, strPathToSequenceDist, imagePrefix, addNoise, argv[4], argv[5]);//
    cout << "completed." << endl;
}

void ImageAfterCRF(string strPathToSequence, string distDir, string imagePrefix, bool addNoise, string sigmas, string sigmac)
{
    if (distDir[distDir.length() - 1] != '/') {
        distDir = distDir + "/";
    }
    distDir += "noise_" + sigmas + "_" + sigmac + "/img/";
    string cmd = "mkdir -p "+distDir;
    system(cmd.data());

    ifstream fTimes;
    string strPathTimeFile = strPathToSequence + "/../times.txt";
    cmd = "cp " + strPathTimeFile + " " + distDir + "../.";
    system(cmd.data());
    string strPathSensorFile = strPathToSequence + "/../sensor.yaml";
    cmd = "cp " + strPathSensorFile + " " + distDir + "../.";
    system(cmd.data());

    ofstream readme(distDir + "../readme.txt");
    readme << "sigma_s of red: " << sigma_red_s << endl;
    readme << "sigma_s of green: " << sigma_green_s << endl;
    readme << "sigma_s of blue: " << sigma_blue_s << endl;
    readme << "sigma_c of red: " << sigma_red_c << endl;
    readme << "sigma_c of green: " << sigma_green_c << endl;
    readme << "sigma_c of blue: " << sigma_blue_c << endl;
    readme.close();

    vector<string> vstrImageFilenames;
    vector<string> vstrNewImageFilenames;
    vector<double> vTimestamps;
    fTimes.open(strPathTimeFile.c_str());
    while(!fTimes.eof())
    {
        string s;
        getline(fTimes,s);
        if(!s.empty())
        {
            stringstream ss;
            ss << s;
            double t;
            ss >> t;
            vTimestamps.push_back(t);
        }
    }

    string strPrefixLeft = strPathToSequence;// + "/img/";

    const int nTimes = vTimestamps.size();
    vstrImageFilenames.resize(nTimes);
    vstrNewImageFilenames.resize(nTimes);

    for(int i=0; i<nTimes; i++)
    {
        stringstream ss;
        ss<<setfill('0') << setw(6) << i;
        vstrImageFilenames[i] = strPrefixLeft + imagePrefix +ss.str() + ".png";
        vstrNewImageFilenames[i] = distDir + imagePrefix + ss.str() + ".png";

        cout<<"processing image "<<i<<" ..."<<endl;

        Mat origin_image = imread(vstrImageFilenames[i]);

        Mat combine_img(480, 640, CV_8UC3);
        for (int j = 0; j < 480; ++j) {
            for (int i = 0; i < 640; ++i) {
                Vec3b tmp_rgb = origin_image.at<Vec3b>(j, i);
                MyRgb a;
                a.red = tmp_rgb[0];
                a.green = tmp_rgb[1];
                a.blue = tmp_rgb[2];
                if(addNoise) {
                    AddGaussianNoise(a, sigma_red_s, sigma_red_c,
                                     sigma_green_s, sigma_green_c, sigma_blue_s, sigma_blue_c, true, false);
                }
                else {
                    AddGaussianNoNoise(a);
                }
                Vec3b resultPixel;
                resultPixel[0]=a.red;
                resultPixel[1]=a.green;
                resultPixel[2]=a.blue;
                combine_img.at<Vec3b>(j, i) = resultPixel;

            }
        }
        imwrite(vstrNewImageFilenames[i], combine_img);
    }
}

void InitSigma()
{
    sigma_red_s   = sigma_s;
    sigma_green_s = sigma_s;
    sigma_blue_s  = sigma_s;
    sigma_red_c   = sigma_c;
    sigma_green_c = sigma_c;
    sigma_blue_c  = sigma_c;
}

void AddGaussianNoNoise(MyRgb& a)
{
    double red_val   = (double)a.red/255.0;
    double green_val = (double)a.green/255.0;
    double blue_val  = (double)a.blue/255.0;

    assert(red_val>=0 && green_val>=0 && blue_val >= 0);

    double irr_red   = spline1dcalc(interpolateIrrgivenbri_r,red_val);
    double irr_green = spline1dcalc(interpolateIrrgivenbri_g,green_val);
    double irr_blue  = spline1dcalc(interpolateIrrgivenbri_b,blue_val);

    irr_red   = min(1.0,max(0.0,irr_red));
    irr_green = min(1.0,max(0.0,irr_green));
    irr_blue  = min(1.0,max(0.0,irr_blue));

    double bri_red   = spline1dcalc(interpolateBrigivenirr_r,irr_red);
    double bri_green = spline1dcalc(interpolateBrigivenirr_g,irr_green);
    double bri_blue  = spline1dcalc(interpolateBrigivenirr_b,irr_blue);

    bri_red   = min(1.0,max(0.0,bri_red));
    bri_green = min(1.0,max(0.0,bri_green));
    bri_blue  = min(1.0,max(0.0,bri_blue));

    a.red   = (unsigned char)(bri_red*255.0);
    a.green = (unsigned char)(bri_green*255.0);
    a.blue  = (unsigned char)(bri_blue*255.0);
}

//sigma_s: irradiance noise
//sigma_c: gause noise
void AddGaussianNoise(MyRgb& a,
                      float sigma_red_s,float sigma_red_c,
                      float sigma_green_s,float sigma_green_c,
                      float sigma_blue_s,float sigma_blue_c,
                      bool noise_flag, bool calc_irr_only)
{

    double red_val   = (double)a.red/255.0;
    double green_val = (double)a.green/255.0;
    double blue_val  = (double)a.blue/255.0;

    assert(red_val>=0 && green_val>=0 && blue_val >= 0);

    double irr_red   = spline1dcalc(interpolateIrrgivenbri_r,red_val);
    double irr_green = spline1dcalc(interpolateIrrgivenbri_g,green_val);
    double irr_blue  = spline1dcalc(interpolateIrrgivenbri_b,blue_val);

    if ( noise_flag )
    {
        std::random_device rd;
        std::default_random_engine generator_(rd());
        std::normal_distribution<double> noise_s_r(0.0, sigma_red_s*sqrt(irr_red));
        std::normal_distribution<double> noise_s_g(0.0, sigma_green_s*sqrt(irr_green));
        std::normal_distribution<double> noise_s_b(0.0, sigma_blue_s*sqrt(irr_blue));

        std::normal_distribution<double> noise_c_r(0.0, sigma_red_c);
        std::normal_distribution<double> noise_c_g(0.0, sigma_green_c);
        std::normal_distribution<double> noise_c_b(0.0, sigma_blue_c);

        double noiser = noise_s_r(generator_);
        double noiseg = noise_s_g(generator_);
        double noiseb = noise_s_b(generator_);
        double noiserc = noise_c_r(generator_);
        double noisegc = noise_c_g(generator_);
        double noisebc = noise_c_b(generator_);
        irr_red   = irr_red   +   noiser  +  noiserc;
        irr_green = irr_green +  noiseg +  noisegc;
        irr_blue  = irr_blue  +  noiseb  +  noisebc;
    }

    irr_red   = min(1.0,max(0.0,irr_red));
    irr_green = min(1.0,max(0.0,irr_green));
    irr_blue  = min(1.0,max(0.0,irr_blue));

    double bri_red   = spline1dcalc(interpolateBrigivenirr_r,irr_red);
    double bri_green = spline1dcalc(interpolateBrigivenirr_g,irr_green);
    double bri_blue  = spline1dcalc(interpolateBrigivenirr_b,irr_blue);

    bri_red   = min(1.0,max(0.0,bri_red));
    bri_green = min(1.0,max(0.0,bri_green));
    bri_blue  = min(1.0,max(0.0,bri_blue));

    if ( !calc_irr_only )
    {
        a.red   = (unsigned char)(bri_red*255.0);
        a.green = (unsigned char)(bri_green*255.0);
        a.blue  = (unsigned char)(bri_blue*255.0);
    }
    else
    {
        a.red   = (unsigned char)irr_red;
        a.green = (unsigned char)irr_green;
        a.blue  = (unsigned char)irr_blue;
    }
}

void GetFileXY(vector<double> &xVector, vector<double> &yVector, string filename)
{
    ifstream infile(filename);

    string line;
    getline(infile, line);//
    int status = 0;
    while(getline(infile, line)) {
        stringstream ss(line);
        int ifExistId = line.find("=");
        if (ifExistId != string::npos) {
            status += 1;
            continue;
        }
        if (status == 0) {
            double tmp;
            for (int i = 0; i < 4; ++i) {
                ss>>tmp;
                xVector.push_back(tmp);
            }
        }
        else if (status == 1) {
            double tmp;
            for (int i = 0; i < 4; ++i) {
                ss>>tmp;
                yVector.push_back(tmp);
            }
        }
        if(status>1) break;
    }
}

spline1dinterpolant GetSpline1dinterpolant(vector<double> &xVector, vector<double> &yVector, bool isLinearCRF)
{
    real_1d_array xx;
    real_1d_array yy;
    spline1dinterpolant s;
    xx.setcontent(xVector.size(), xVector.data());
    yy.setcontent(yVector.size(), yVector.data());
    if (isLinearCRF) {
        spline1dbuildlinear(xx, xx, s);
    }
    else {
        spline1dbuildlinear(xx, yy, s);
    }

    return s;
}

void GetParameter(string emorName,string invemorName)
{
    GetFileXY(emorE0, emorF0, emorName);
    GetFileXY(emorB0, emorG0, invemorName);

    interpolateIrrgivenbri_r = GetSpline1dinterpolant(emorB0, emorG0, isLinearCRF);
    interpolateIrrgivenbri_g = GetSpline1dinterpolant(emorB0, emorG0, isLinearCRF);
    interpolateIrrgivenbri_b = GetSpline1dinterpolant(emorB0, emorG0, isLinearCRF);

    interpolateBrigivenirr_r = GetSpline1dinterpolant(emorE0, emorF0, isLinearCRF);
    interpolateBrigivenirr_g = GetSpline1dinterpolant(emorE0, emorF0, isLinearCRF);
    interpolateBrigivenirr_b = GetSpline1dinterpolant(emorE0, emorF0, isLinearCRF);

}
