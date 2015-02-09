function create_idx()
{
    local table=$2
    local db=$1
    shift 2
    local args=$@
    echo 'create index '$args' for table '$table' db '$db
    echo 'db.'$table'.ensureIndex('$args')'|mongo localhost:27017/$db
}
create_idx content_db info '{"id":1}'
create_idx content_db info '{"pub_time":-1}'
create_idx content_db info '{"stat":1,"cat":1}'
create_idx content_db info '{"cat":1,"id":1,"score":1}'
create_idx content_db info '{"type":1,"id":1,"score":1}'
create_idx content_db info '{"location":1,"cat":1}'
create_idx app_db info '{"id":1}'
create_idx content_index info '{"term":1}'
create_idx content_db not_access '{"id":1}'
