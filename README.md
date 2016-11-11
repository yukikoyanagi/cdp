# CDP analysis
These are the scripts used for the CDP analysis.

## Software requirements
1. GSL: Need 1.16 or above. On grendel we can do 'module load gsl/2.0'
2. Intel compiler: Not sure about the version, but on grendel scripts did not run until we did 'module load intel/16.0.2.181'
3. Python: Need 2.7.12. On grendel we can do 'module load python/2.7.12'
4. perl: Required 5.10.1. Recommended 5.14.2 (this is the version on spencer). If installing without root privilege, an easy way is to use perlbrew <https://perlbrew.pl/>. After installing perlbrew and the appropriate version of perl (see the instruction on the website), do 'perlbrew switch perl-5.4.12' to set default version.
5. perl modules: Need File::Slurp and Math::GSL. The easiest way, if perl was installed with perlbrew as above, is to use cpanm. Do 'perlbrew install-cpanm' to install cpanm, and then 'cpanm install File::Slurp' and 'cpanm install Math::GSL'.

## Data requirements
The dataset used for analysis is described in QGM Aarhus' DropBox.  But the scripts assume some things about the data structure.  The protein files should be archived in a file called prot.tar.bz2, with the directory structure prot/{protein id}.txt. The option files should be called step\*\_opts and should be archived in a file called opts.tar.bz2, with the directory structure opts/step\*\_opts. 

*The following applies when running analysis with cdp.sh or cdp_prll.sh* 

The scripts should be archived in a file called cdp.tar.bz2. `make_cdp_tar.sh` can be used to do this.

## To run the analysis on grendel
1. Copy prot.tar.bz2, opts.tar.bz2, cdp.tar.bz2 and cdp.sh files to grendel (e.g. ~/cdp).
2. Ensure the parameters in cdp.sh file are correct (email address, walltime, etc.)
3. Send the job with qsub.
4. It will produce files called step\*.tar.bz2, containing opts file, clustering summary and the assessment file.
5. tar all ste'\*.tar.bz2 files and send it to spencer:~/grendel/[some directory]

 *The following steps can be performed on spencer (or own machine)*

6. cd into spencer:~/grendel
7. Run './postprocess.sh [path to tar file]. This creates 4 output txt files in the same directory as the tar file. They are;

 prediction.txt: Raw prediction data

 stat_out200_so3.txt: Summary statistics for all bonds

 stat_L_out200_so3.txt: Summaty statistics for long-range bonds

 stat_nonL_out200_so3.txt: Summary statistics for non-long bonds
