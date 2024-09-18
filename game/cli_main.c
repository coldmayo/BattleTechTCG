// I got the idea for this from a crackme I did once

#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <stdbool.h>
#include <stdlib.h>

void show_select(int choice) {
    printf("\e[1;1H\e[2J");
	char * opts[4];
	opts[0] = "[1]--|Train Model";
	opts[1] = "[2]--|Play Model";
	opts[2] = "[3]--|Search Cards";
	opts[3] = "[4]--|Make Deck";
	
	for (int i = 0; i < 4; i++) {
		if (choice == i) {
    		printf(" { %s }\n", opts[i]);
		} else {
			printf("%s\n", opts[i]);
		}
	}
	printf("[5]--|Exit\n");
	printf("Press 1-4 to select and Enter to select: ");
}

void execute(int choice) {
    printf("\e[1;1H\e[2J");
	switch(choice) {
		case 0:
    		system("cd ../AI ; ./train.sh");
    		sleep(2);
    		break;
    	case 1:
        	printf("In construction\n");
            sleep(2);
        	break;
        case 2:
            printf("In construction\n");
			sleep(2);
            break;
        case 3:
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
				return 0;
		}
	}
	
}
