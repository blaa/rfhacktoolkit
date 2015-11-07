/****************************************************************************** 
 * Signal replicator based on PiHAT radio module which was based on PIFM.     * 
 *                                                                            * 
 * Use of this application is solely at your own risk!                        * 
 *                                                                            * 
 * Original PiFm-project: http://www.icrobotics.co.uk/wiki/index.php/         * 
 *                        Turning_the_Raspberry_Pi_Into_an_FM_Transmitter     * 
 *                                                                            * 
 * PiHAT project: http://skagmo.com -> Projects -> PiHAT                      * 
 *                                                                            * 
 ******************************************************************************/

#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <sys/time.h>
#include <time.h>

#include "radio.h"

void ook_transmit(const char *filename, int mod) 
{
	FILE *fd = fopen(filename, "r");
	char cmd;
	int arg;	
	int ret;
	struct timespec ts;

	if (!fd) {
		printf("ERROR: Unable to open data file\n");
		return;
	}

	/* Calculate total tx time for calibration */
	float took = 0;
	struct timeval start, stop;
	gettimeofday(&start, NULL);

	while (!feof(fd)) {
		fscanf(fd, "%c%d\n", &cmd, &arg);
		//printf("%c %d\n", cmd, arg);
		switch (cmd) {
		case 'N':
			if (arg == 0) {
				continue;
			} 
			//printf("Sleep for %ld\n", ts.tv_nsec);
			//for (int X = 0; X < arg/162; X ++) {
        		//	ACCESS(CM_GP0DIV) = (0x5a << 24) + mod  + (X/8)%3 - 1 ;
				// Going for 0.077
			//}
			
			ts.tv_sec = 0;
			ts.tv_nsec = arg - 80000;
			ret = nanosleep(&ts, NULL);	
			if (ret != 0) {
				printf("Warning nanosleep returned != 0: %d\n", ret);
				perror("nanosleep");
				return;
			}
			
			continue;
		case 'S': 
			if (arg) {
				//printf("TX 1\n");
				askHigh();
			} else {
				//printf("TX 0\n");
				askLow();
			}
			continue;
		default:
			printf("ERROR: Invalid command in data file: %c\n", cmd);
			return;
		}
	}
	gettimeofday(&stop, NULL);
	took = (stop.tv_sec - start.tv_sec) * 1e6;
	took += (stop.tv_usec - start.tv_usec);
	took /= 1e6;	
	printf("Transmission took %10.5f\n", took);
	fclose(fd);
	return;
}

int set_freq(float freq, int dev)
{
	/* Configure frequency */
	/*
	 * 144.64 -> 433.933 measured (27ppm, not calibrated)
         * My pilot is at 433.8 measured 
	 */

	printf("Tuning to base freq %.3f + %d with harmonics: %.3f %.3f %.3f\n", freq, dev, freq*2, freq*3, freq*4);
        int mod = (500.0*4096.) / freq;
	mod += dev;

	float freq_back = (500.0 * 4096.0)/mod;
	printf("Frequency after rounding %.3f with harmonics: %.3f %.3f %.3f\n", freq_back, freq_back*2, freq_back*3, freq_back*4);
	
        ACCESS(CM_GP0DIV) = (0x5a << 24) + mod;
	//ACCESS(CM_GP0DIV) = (0x5a << 24) + 0x374F; // Tune to 144.64 MHz to get the third harmonic at 433.92 MHz
	return mod;
}


void transmit_repeat(const char *fname, float freq) 
{
	int mod;
	int dev = -2;
	int i = 0;
	set_freq(freq, dev);
	askLow();
	usleep(10000);
	
	//for (; dev<=2; dev++) {
	//	for (int i=0; i<1; i++) {
			mod = set_freq(freq, dev);		

			printf("TX dev=%d try %d\n", dev, i);
			ook_transmit(fname, mod);
			usleep(25000);
	//	}
	//}

}

int main (int argc, char **argv)
{
	/* Setup RF-configuration */
	setup_io();
	setup_fm();

	char *fname = argv[1];
	if (!fname) {
		printf("Pass data file as first and only argument\n");
		return -1;
	}

	printf("Reading signal data from %s\n", fname);

	
        //float freq = 433.800;
        float freq = 433.917;
	transmit_repeat(fname, freq / 3.0);
	//transmit_repeat(fname, freq / 4.0);
	//transmit_repeat(fname, freq / 5.0);
	//transmit_repeat(fname, freq / 6.0);
	//transmit_repeat(fname, freq / 8.0);
	//transmit_repeat(fname, freq / 11.0 + 0.02/11.0);

	printf("Shutting down transmission\n");
	askLow();
	return 0;
}

