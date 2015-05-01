#include "XXTEA.h"
#include <iostream>
#include "stdio.h"
#include "stdlib.h"

void encryptFile(std::string filename, std::string key)
{
	unsigned int size;
	FILE *fp = fopen(filename.c_str(), "rb");
	if (!fp)
	{
		printf("file open failed %s", filename.c_str());
		return;
	}
	

	fseek(fp,0,SEEK_END);
	size = ftell(fp);
	fseek(fp,0,SEEK_SET);
	unsigned char* pBuffer = new unsigned char[size];
	size= fread(pBuffer,sizeof(unsigned char), size,fp);
	fclose(fp);

	unsigned char* p = xxtea_encrypt(pBuffer, size, (unsigned char*)key.c_str(), key.length(), &size);
	fp = fopen(filename.c_str(), "wb");
	if (!fp)
	{
		printf("file open failed %s", filename.c_str());
		return;
	}
	//printf("xxtea_encrypt succ --%s-- size %d\n", p, size);
	fwrite(p, 1,size, fp);
	fclose(fp);
}

void decryptFile(std::string filename, std::string key)
{
	unsigned int size;
	FILE *fp = fopen(filename.c_str(), "rb");
	if (!fp)
	{
		printf("file open failed %s\n", filename.c_str());
		return;
	}


	fseek(fp,0,SEEK_END);
	size = ftell(fp);
	fseek(fp,0,SEEK_SET);
	unsigned char* pBuffer = new unsigned char[size];
	size= fread(pBuffer,sizeof(unsigned char), size,fp);
	fclose(fp);

	//printf("xxtea_decrypt  --%s-- size  %d\n", pBuffer, size);

	unsigned char* p = xxtea_decrypt(pBuffer, size, (unsigned char*)key.c_str(), key.length(), &size);
	//printf("xxtea_decrypt end  --%s--", p);
	fp = fopen(filename.c_str(), "wb");
	if (!fp)
	{
		printf("file open failed %s\n", filename.c_str());
		return;
	}
	fwrite(p, 1,size, fp);
	fclose(fp);
}

int  main ( int arc, char **argv ) {
     // code
	if (arc < 3)
	{
		return 0;
	}
	std::string filename = argv[2];
	std::string key = argv[3];
	int t = atoi(argv[1]);
	if (t == 1)
	{
		encryptFile(filename, key);
	}
	else
	{
		decryptFile(filename, key);
	}
     //for(int i = 0; i < arc; ++i)
     //{
     //   printf("\nArgument %d is %s.", i, argv[i]);
     //}
     return 0; // Indicates that everything vent well.
}