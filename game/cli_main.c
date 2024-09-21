// I got the idea for this from a crackme I did once

#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <stdbool.h>
#include <stdlib.h>
#include "searchCard.h"

void show_select(int choice) {
    printf("\e[1;1H\e[2J");
	char * opts[5];
	opts[0] = "[1]--|Set up Envirenment";
	opts[1] = "[2]--|Train Model";
	opts[2] = "[3]--|Play Model";
	opts[3] = "[4]--|Search Cards";
	opts[4] = "[5]--|Make Deck";
	
	for (int i = 0; i < 5; i++) {
		if (choice == i) {
    		printf(" { %s }\n", opts[i]);
		} else {
			printf("%s\n", opts[i]);
		}
	}
	printf("[6]--|Exit\n");
	printf("Press 1-6 to select and Enter to select: ");
}

void execute(int choice) {
    printf("\e[1;1H\e[2J");
	switch(choice) {
    	case 0:

        	bool makeVenv;
        	char buff;
        	printf("Starting installation...\n");
        	if (access("../AI/.venv/bin/activate", F_OK) == 0) {
				printf("Virtual Envirenment already installed!\n");
				printf("Would you like to reinstall it? (y/n): ");
				while (true) {
					fgets(&buff, 100, stdin);
					if (buff == 'y' || buff == 'Y') {
						makeVenv = true;
						break;
					} else if (buff == 'n' || buff == 'N') {
						makeVenv = false;
						break;
					} else {
						printf("The acceptable answers are y and n: ");
					}
				}
				
        	} else {
				printf("Virtual Envirement does not exist, generating...\n");
				makeVenv = true;
        	}

        	if (makeVenv) {
				system("python -m venv ../AI/.venv");
        	}
        	printf("Installing packages...\n");
        	system("source ../AI/.venv/bin/activate; pip install ../AI/gym_mod/");
			printf("Done!");
			sleep(2);
        	break;
		case 1:
    		system("cd ../AI ; ./train.sh");
    		sleep(2);
    		break;
    	case 2:
        	printf("In construction\n");
            sleep(2);
        	break;
        case 3:
            search_card();
            break;
        case 4:
            printf("In construction\n");
            sleep(2);
            break;
	}
}

int main() {
	int choice = 0;
	char buff;
	while (true) {
		
		show_select(choice);

		buff = getchar();
		switch(buff) {
			case '\n':
				execute(choice);
				break;
			case '1':
				choice = 0;
				show_select(choice);
				break;
			case '2':
				choice = 1;
				show_select(choice);
				break;
			case '3':
				choice = 2;
				show_select(choice);
				break;
			case '4':
				choice = 3;
				show_select(choice);
				break;
			case '5':
				choice = 4;
				show_select(choice);
				break;
			case '6':
				return 0;
		}
	}
	
}
