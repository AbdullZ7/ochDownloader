//compiled using Visual C++ Express 2010

#include "stdafx.h"
#include <string>
#include <cstdlib>
#include <iostream>
#include <fstream>
#include <stdio.h>
#include <stdlib.h>
#include <winsock2.h>
#pragma comment(lib, "ws2_32.lib")

#include <windows.h>

using namespace std;
using namespace System;


int main(int argc, char* argv[])
{
	string opts;
	string space = " ";

	for (int i = 1; i < argc; i++)
		opts = opts + argv[i] + space;

	//cout << opts << endl;

    //initializing winsock 2.2
	WSADATA wsadata;
	if(WSAStartup(MAKEWORD(2,2), &wsadata) != 0)
	{
		WSACleanup();
		return 1;
	}

	//create socket
	SOCKET c_sock;
	if((c_sock = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP)) == INVALID_SOCKET)
	{
		WSACleanup();
		return 1;
	}
	
	//resolving host/server
	char hostname[40] = "localhost";
	struct hostent *host;
	if((host = gethostbyname(hostname)) == NULL)
	{
		WSACleanup();
		return 1;
	}
	
	//read port from file
	char buffer[MAX_PATH];
	GetModuleFileNameA(NULL, buffer, MAX_PATH); //windows only
	string f = string(buffer);
	f = f.substr(0, f.find_last_of("\\/")); //remove file name (../bin/port.txt)
	f = f.substr(0, f.find_last_of("\\/")); //go down one level (../port.txt)
	string file_port_path = f + "\\port.txt";

	ifstream infile(file_port_path);
    string line;
	getline(infile, line);
	infile.close();
	int port;
	port = atoi(line.c_str());
	
	//prepare server sockaddr_in structure
	SOCKADDR_IN server;
	server.sin_family = AF_INET;
	server.sin_port = htons(port);
	server.sin_addr.s_addr = *(unsigned long*)host->h_addr;

	//connect to server
	if(connect(c_sock, (SOCKADDR *) &server, sizeof(server)) == SOCKET_ERROR)
	{
		//int error = WSAGetLastError();
		WSACleanup();
		return 1;
	}
	
	//send to server
	//char *msg = "Hola...";
	send(c_sock, opts.c_str(), opts.length(), 0);
	
	//shutdown socket
	shutdown(c_sock, SD_SEND);
	
	//close socket entirly
	closesocket(c_sock);
	
	//clean winsock
	WSACleanup();
	
	return 0;
}
