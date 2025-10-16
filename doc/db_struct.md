```mermaid
erDiagram
    users {
        bigint id PK
        varchar email
        varchar username
        varchar password_hash
        timestamptz created_at
        timestamptz last_login
        boolean is_active
        text profile_text
        varchar avatar_path
    }
    
    posts {
        bigint id PK
        bigint user_id FK
        varchar post_title
        text post_content
        timestamptz created_at
        timestamptz modified_at
        boolean is_published
        integer view_counter
    }
    
    tags {
        bigint id PK
        varchar tag_name
        text tag_description
        timestamptz created_at
    }
    
    comments {
        bigint id PK
        bigint post_id FK
        bigint user_id FK
        bigint parent_comment_id FK
        text comment_text
        timestamptz created_at
        timestamptz updated_at
        boolean was_edited
    }
    
    bookmarks {
        bigint user_id PK,FK
        bigint post_id PK,FK
        timestamptz saved_at
    }
    
    user_subscriptions {
        bigint follower_id PK,FK
        bigint following_id PK,FK
        timestamptz subscribed_at
    }
    
    post_reactions {
        bigint user_id PK,FK
        bigint post_id PK,FK
        timestamptz reacted_at
    }
    
    post_tags {
        bigint post_id PK,FK
        bigint tag_id PK,FK
        timestamptz added_at
    }

    users ||--o{ posts : "создает"
    users ||--o{ comments : "пишет"
    users ||--o{ bookmarks : "сохраняет"
    users ||--o{ user_subscriptions : "подписывается"
    users ||--o{ user_subscriptions : "на него подписываются"
    users ||--o{ post_reactions : "лайкает"
    posts ||--o{ comments : "комментируется"
    posts ||--o{ bookmarks : "в закладках"
    posts ||--o{ post_reactions : "лайки"
    posts }o--|| post_tags : "имеет теги"
    tags }o--|| post_tags : "используется в постах"
    comments ||--o{ comments : "ответы"