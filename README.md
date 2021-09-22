# telegrambot

Criei esse bot para gerenciar alguns canais de telegram que sou administrador. Preferi não utilizar nenhum wrapper já conhecido da API (como o python-telegram-bot) e criar o meu próprio, mas por enquanto não tem tantos comandos.

No momento o bot atende os seguintes comandos:
```
!help: lista de comandos disponíveis
!mod <username>: adiciona o usuário na lista de moderadores *
!unmod <username>: remove o usuário da lista de moderadores *
!mute <username> <tempo em segundos>: adiciona o usuário na lista de silenciados pelo tempo especificado **
!unmute <username>: remove o usuário da lista de silenciados **
!add <comando> | <resposta> | <descrição>: adiciona um novo comando (para mídias, enviar o comando na legenda) **
!del <comando>: remove um comando customizado *

* necessário ser um administrador
** necessário ser um administrador ou moderador
```
Para o bot identificar o usuário pelo username, ele precisa indexar esse usuario no banco. Pra fazer isso, sempre que vai verificar as novas mensagens do canal, ele valida se o usuario que enviou a mensagem já está na lista de usuários conhecidos, e quando o usuário nao é encontrado ele adiciona ao banco e insere na lista de usuários conhecidos.

Qualquer duvida, report de bugs, sugestões de melhorias pode entrar em contato comigo por issue. :)




