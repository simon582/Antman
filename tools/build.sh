function run_command()
{
    local db=$1
    local cmd=$2
    echo "================== cmd "$cmd" ================================="
    echo $cmd|mongo localhost:27017/$db|egrep -v "MongoDB|connecting|bye"
}
function count_table()
{
    local db=$1
    local table=$2
    run_command $db "db.$table.count()"
}

function create_idx()
{
    local table=$2
    local db=$1
    shift 2
    local args=$@
    echo 'create index '$args' for table '$table' db '$db
    echo 'db.'$table'.ensureIndex('$args')'|mongo localhost:27017/$db
}
function build()
{
    #python transform.py content_db info_temp info run 0 0 >> ../log/transform.out 2>> ../log/transform.err
    bash transform.sh
    #python transform.py content_db info_weibo_temp content_db info run 0 0 >> ../log/transform_weibo.out 2>> ../log/transform_weibo.err
    python transform.py goods_db info goods_db info run 0 0 handle_rm_old_data >> ../log/rm_old_data.out 2>> ../log/rm_old_data.err
    python rm_duplicate.py 0 1 content_db info >> ../log/rm_duplicate.out 2>> ../log/rm_duplicate.err
    python transform.py goods_db info goods_db info run 0 0 handle_pre_pub >> ../log/pre_pub.out 2>> ../log/pre_pub.err
    #python build_index.py gennew >> ../log/build_index.out 2>>../log/build_index.err
    #run_command content_index 'db.info.renameCollection("info_old")'
    #run_command content_index 'db.info_new.renameCollection("info")'
    #create_idx content_index info '{"term":1}'
    #run_command content_index 'db.info_old.drop()'
    #count_table content_index info
}
build
#count_table content_index info
