# telegrambot

Criei esse bot para gerenciar alguns canais de telegram que sou administrador. Preferi não utilizar nenhum wrapper já conhecido da API (como o python-telegram-bot) e criar o meu próprio, mas por enquanto não tem tantos comandos.

No momento o bot atende os seguintes comandos 

## Gerenciador de Grupo:
```
/help: lista os comandos disponíveis no grupo
/mod <username>: promove o usuário ao cargo de moderador *
/unmod <username>: rebaixa o usuário do cargo de moderador *
/mute <username> <tempo em segundos>: adiciona o usuário na lista de silenciados pelo tempo especificado **
/unmute <username>: remove o usuário da lista de silenciados **
/cmd: lista os comandos customizados disponíveis no grupo
/addcmd <comando> | <resposta> | <descrição>: adiciona um novo comando (para mídias, enviar o comando na legenda) **
/delcmd <comando>: remove um comando customizado *

* necessário ser um administrador (do bot)
** necessário ser um administrador ou moderador
```

Para o bot identificar o usuário pelo username, ele precisa indexar esse usuario no banco. Pra fazer isso, sempre que vai verificar as novas mensagens do canal, ele valida se o usuario que enviou a mensagem já está na lista de usuários conhecidos, e quando o usuário nao é encontrado ele adiciona ao banco e insere na lista de usuários conhecidos.

## Monitor de Promoções

Com o tempo, adicionei uma funcionalidade para que ele monitore promoçoes e notifique os usuários. Para utilizar essa funcionalidade veja os comandos abaixo:
```
/help: lista os comandos disponíveis no chat privado
/promo: lista as promoções cadastradas pelo usuário
/addpromo <palavra-chave> | <opcional:valor-máx>: monitora e notifica promoções referentes a palavra-chave (caso não seja passado o valor máximo, todas as promoções são notificadas)
/delpromo <palavra-chave>: remove a palavra-chave da lista de monitoramento de promoções
/clearpromo: remove todas as palavras-chave da lista de monitoramento de promoções
```

## Rodando com docker-compose:
entrar na pasta raiz do repositório e executar: 
docker-compose up --build -d

Qualquer duvida, report de bugs, sugestões de melhorias pode entrar em contato comigo por issue. :)




