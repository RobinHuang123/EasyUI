
Vue.component('easy-comp', {
    template: '<component :is="comp" :name="name" :x="x" :y="y"></component>',
    props: ['comp', 'name', "x", "y", "z", "width", "height", "cid", 'api'],
})

Vue.component('not-found-404', {
    template: '<el-card>404</el-card>',
})


Vue.component('easy-main', {
    template:`
<el-main :style='{height: scrollerHeight}'>
    <template v-for="(row, x) in comps">
        <el-row :gutter="10">
            <template v-for="(col, y) in row">
                <el-col :span="col_width(col)" >
                    <template v-for="(col_z, z) in col">
                        <template v-if="col_z.card">
                            <el-card shadow="hover">
                            <easy-comp :is=col_z.vue :name=x :x=x :y=y :z=z :width=col_z.width :height=col_z.height :cid="uid" :api=col_z.api></easy-comp>
                            </el-card>
                        </template>
                        <template v-else>
                            <easy-comp :is=col_z.vue :name=x :x=x :y=y :z=z :width=col_z.width :height=col_z.height :cid="uid" :api=col_z.api></easy-comp>
                        </template>
                    </template>
                </el-col>
            </template>
        </el-row>
        <el-row>&nbsp</el-row>
    </template>
</el-main>
    `,
    props: ['opts', 'cid'],
    data: function () {
        return {
            uid: -1,
            comps: this.get_comps(),
        }
    },
    watch: {
        cid: function (new_value) {
            console.log("easy-main cid changed", new_value)
            this.uid++
        },
        uid: function (new_value) {
            console.log("easy-main uid changed", new_value)
            this.comps = this.get_comps()
            console.log("this.data.comps", this.comps)

        }
    },
    created: function () {
        console.log("created easy-main", this.opts)
    },
    methods: {
        isArray: function(x) {
            if (Array.isArray(x)) {
                console.log(x)
            }
            return Array.isArray(x)
        },
        col_width: function(col) {
            var w = 0
            for (var z in col) {
                if (w < col[z].width) {
                    w = col[z].width
                }
            }
            return w
        },
        get_page_by_name: function(name)  {
            for (var x in this.opts) {
                page = this.opts[x]
                if (page.name == name) {
                    return page.comps
                }
            }
            return null
        },
        get_comps: function() {
            console.log("currentPage", this.opts.currentPage)
            if (this.opts.currentPage != undefined) {
                var comp_root = this.get_page_by_name(this.opts.currentPage)
                console.log("comp_root == ", comp_root)
                var layout = Array()
                if (Array.isArray(comp_root)) {
                    for (var x in comp_root) {
                        if (Array.isArray(comp_root[x])) {
                            var cols = Array()
                            for (var y in comp_root[x]) {
                                if (Array.isArray(comp_root[x][y])) {
                                    cols.push(comp_root[x][y])
                                } else {
                                    cols.push([comp_root[x][y]])
                                }
                            }
                            layout.push(cols)
                        } else {
                            layout.push([[comp_root[x]]])
                        }
                    }
                } else {
                    layout.push([[comp_root]])
                }
                return layout
            } else {
                return [[[{vue: 'not-found-404', width: 24 }]]]
            }
        },
    },
    computed: {

        scrollerHeight: function() {
            // header 60px, footer60px
            return (window.innerHeight - 140) + 'px';
        }
    }
})

