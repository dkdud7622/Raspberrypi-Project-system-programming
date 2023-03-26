#include <arpa/inet.h>
#include <stdio.h>
#include <string.h>
#include <sys/socket.h>
#include <unistd.h>
#include <string.h> // strstr 함수가 선언된 헤더 파일

#define TF_PORT 7040
#define SERVER_PORT 4080
void error_handling(char *message)
{
    fputs(message, stderr);
    fputc('\n', stderr);
    _exit(1);
}

int connectModelServer(int &sock)
{
    int valread, client_fd;
    int offset  = 0;
    struct sockaddr_in serv_addr;
    char buffer[1024] = {0};
    if ((sock = socket(AF_INET, SOCK_STREAM, 0)) < 0)
    {
        printf("\n Socket creation error \n");
        return -1;
    }

    serv_addr.sin_family = AF_INET;
    serv_addr.sin_port = htons(TF_PORT);

    // Convert IPv4 and IPv6 addresses from text to binary
    // form
    if (inet_pton(AF_INET, "127.0.0.1", &serv_addr.sin_addr) <= 0)
    {
        printf("\nInvalid address/ Address not supported \n");
        return -1;
    }

    if ((client_fd = connect(sock, (struct sockaddr *)&serv_addr, sizeof(serv_addr))) < 0)
    {
        printf("\nConnection Failed \n");
        return -1;
    }

    return client_fd;
}

int closeModelServer(int sock)
{
    return close(sock);
}

double getDistance()
{
    char buffer[1024];
    char *ptrBuffer = buffer;
    int sock = 0;
    int client_fd = connectModelServer(sock);
    if (client_fd < 0)
    {
        return -1;
    }

    int index = 0;
    do
    {
        index += read(sock, buffer + index, 10);
        buffer[index] = '\0';
    } while (strstr(ptrBuffer, "\r\n") == NULL && index >= 1000);

    double distance;
    sscanf(buffer, "%lf", &distance);

    closeModelServer(sock);
    return distance;
}

int connectClient()
{
    int serv_sock, clnt_sock = -1;
    struct sockaddr_in serv_addr, clnt_addr;
    socklen_t clnt_addr_size;

    //소켓 생성
    serv_sock = socket(PF_INET, SOCK_STREAM, 0);
    if (serv_sock == -1)
        error_handling("socket() error");

    //정보설정. portnum = 2080
    memset(&serv_addr, 0, sizeof(serv_addr));
    serv_addr.sin_family = AF_INET;
    serv_addr.sin_addr.s_addr = htonl(INADDR_ANY);
    serv_addr.sin_port = htons(SERVER_PORT);

    if (bind(serv_sock, (struct sockaddr *)&serv_addr, sizeof(serv_addr)) == -1)
        error_handling("bind() error");
    if (listen(serv_sock, 5) == -1)
        error_handling("listen() error");
    if (clnt_sock < 0)
    {
        clnt_addr_size = sizeof(clnt_addr);
        clnt_sock = accept(serv_sock, (struct sockaddr *)&clnt_addr,
                           &clnt_addr_size);
        if (clnt_sock == -1)
            error_handling("accept() error");
    }
    return clnt_sock;
}

int main(int argc, char const *argv[])
{
    printf("server start\n");
    int str_len;
    int request = 0;
    int count = 0;
    int msg;
    int clnt_sock = connectClient();
    printf("connected\n");
    while (1)
    {
        printf("here %d\n",request);
        str_len = read(clnt_sock, &request, sizeof(request));
        printf("end read %d\n",request);
        if (str_len == -1)
        {
            printf("%d str_len=-1\n",request);
            error_handling("read() error");
        }
        if (request == 1)
        {
            int distance = getDistance()*100;
            printf("distance writing\n");
            write(clnt_sock,&distance, sizeof(distance));
            printf("distance writed\n");
            printf("%d\n",distance);
            request = 0;
            count =0;
        }
        //count +=1;
        printf("out %d\n",request);
    } 
    
    return 0;
}
