// 408 考研标杆院校与江浙沪精细化专业数据库 (精准标注 11408 vs 22408、学费住宿与官方出处)
export const collegesData = [
    // ===== 1. 江浙沪【稳健 22408 梯队】(数二 + 英二 + 408，保宿舍+常规学费) =====
    { 
        name: "中国矿业大学 (徐州)", 
        major: "081200(11408) | 085400计专(22408)",
        region: "江浙沪",
        cat: "211", tag: "tag-211", level: "江苏优质211/性价比之王", 
        subject: "22408 (数二+英二)",
        y2023: "310分 / 均342分", y2024: "315分 / 均348分", y2025: "318分 / 均350分",
        tuition: "8000 元/年", dorm: "保障校内宿舍 (约1200/年)", dorm_type: "tag-dorm", ratio: "1:5 (极友好)",
        pub_date: "2025-09-15", source: "矿大研招简章", url: "http://yjsy.cumt.edu.cn/" 
    },
    { 
        name: "苏州大学", 
        major: "081200(11408) | 085404计专(22408)",
        region: "江浙沪",
        cat: "211", tag: "tag-211", level: "江苏强势211/就业极佳", 
        subject: "22408 (数二+英二)",
        y2023: "325分 / 均355分", y2024: "330分 / 均360分", y2025: "332分 / 均362分",
        tuition: "8000 元/年", dorm: "保障校内宿舍 (约1200/年)", dorm_type: "tag-dorm", ratio: "1:7 (热门)",
        pub_date: "2025-09-18", source: "苏大研究生院", url: "http://yjsy.suda.edu.cn/" 
    },
    { 
        name: "江南大学 (无锡)", 
        major: "081200(11408) | 085404计专(22408)",
        region: "江浙沪",
        cat: "211", tag: "tag-211", level: "江苏优质211/稳健优选", 
        subject: "22408 (数二+英二)",
        y2023: "320分 / 均350分", y2024: "325分 / 均355分", y2025: "326分 / 均356分",
        tuition: "10000 元/年", dorm: "保障校内宿舍 (约1200/年)", dorm_type: "tag-dorm", ratio: "1:6 (适中)",
        pub_date: "2025-09-16", source: "江南大学研招网", url: "http://yz.jiangnan.edu.cn/" 
    },
    { 
        name: "南京邮电大学", 
        major: "081200(11408) | 085404计专(22408)",
        region: "江浙沪",
        cat: "double", tag: "tag-double", level: "双一流/IT通信巨头", 
        subject: "22408 (数二+英二)",
        y2023: "310分 / 均338分", y2024: "318分 / 均345分", y2025: "315分 / 均342分",
        tuition: "10000 元/年", dorm: "保障校内宿舍 (仙林校区)", dorm_type: "tag-dorm", ratio: "1:5 (2026改408)",
        pub_date: "2025-09-17", source: "南邮计院公示", url: "http://yz.njupt.edu.cn/" 
    },
    { 
        name: "华东理工大学 (上海)", 
        major: "081200(11408) | 085404计专(22408)",
        region: "江浙沪",
        cat: "211", tag: "tag-211", level: "上海优质211/常规学费", 
        subject: "22408 (数二+英二)",
        y2023: "328分 / 均355分", y2024: "335分 / 均362分", y2025: "332分 / 均360分",
        tuition: "10000 元/年", dorm: "提供宿舍 (徐汇/奉贤)", dorm_type: "tag-dorm", ratio: "1:6 (2025改408)",
        pub_date: "2025-09-19", source: "华理信息学院", url: "http://e.ecust.edu.cn/" 
    },
    { 
        name: "上海电力大学", 
        major: "085404 计算机技术专硕",
        region: "江浙沪",
        cat: "double", tag: "tag-double", level: "国家电网VIP高校/极高就业", 
        subject: "22408 (数二+英二)",
        y2023: "298分 / 均326分", y2024: "305分 / 均332分", y2025: "302分 / 均330分",
        tuition: "8000 元/年", dorm: "保障校内宿舍 (临港校区)", dorm_type: "tag-dorm", ratio: "1:4 (电网就业高薪)",
        pub_date: "2025-09-16", source: "上电研招网", url: "http://yjsc.shiep.edu.cn/" 
    },
    { 
        name: "江苏大学 (镇江)", 
        major: "081200(11408) | 085400计专(22408)",
        region: "江浙沪",
        cat: "double", tag: "tag-double", level: "江苏老牌工科/稳妥兜底", 
        subject: "22408 (数二+英二)",
        y2023: "290分 / 均318分", y2024: "298分 / 均325分", y2025: "295分 / 均322分",
        tuition: "8000 元/年", dorm: "保障校内宿舍 (约1000/年)", dorm_type: "tag-dorm", ratio: "1:3 (安全兜底)",
        pub_date: "2025-09-15", source: "江大研招网", url: "http://yz.ujs.edu.cn/" 
    },

    // ===== 2. 医工交叉/中医药黄金赛道 (均为 22408) =====
    { 
        name: "南京医科大学", 
        major: "085404 计专 (生医工程与信息学院)",
        region: "江浙沪",
        is_med: true,
        cat: "double", tag: "tag-double", level: "医工交叉/医学AI黄金赛道", 
        subject: "22408 (数二+英二)",
        y2023: "310分 / 均335分", y2024: "318分 / 均342分", y2025: "315分 / 均340分",
        tuition: "8000 元/年", dorm: "保障校内宿舍 (约1200/年)", dorm_type: "tag-dorm", ratio: "1:4 (中医药背景极友好)",
        pub_date: "2025-09-18", source: "南医大研究生院", url: "http://yjsy.njmu.edu.cn/" 
    },
    { 
        name: "中国药科大学", 
        major: "085404 计专 (计算机与信息工程系)",
        region: "江浙沪",
        is_med: true,
        cat: "211", tag: "tag-211", level: "药学顶级211/生物医药AI", 
        subject: "22408 (数二+英二)",
        y2023: "312分 / 均338分", y2024: "320分 / 均345分", y2025: "318分 / 均344分",
        tuition: "9000 元/年", dorm: "保障校内宿舍 (江宁校区)", dorm_type: "tag-dorm", ratio: "1:4.5 (导师青睐工科)",
        pub_date: "2025-09-17", source: "药大研招目录", url: "http://yjsy.cpu.edu.cn/" 
    },
    { 
        name: "南京中医药大学", 
        major: "085404 计专 (人工智能与信息技术学院)",
        region: "江浙沪",
        is_med: true,
        cat: "double", tag: "tag-double", level: "本校保底/导师人脉主场", 
        subject: "22408 (数二+英二)",
        y2023: "280分 / 均305分", y2024: "288分 / 均312分", y2025: "285分 / 均310分",
        tuition: "8000 元/年", dorm: "保障校内宿舍 (仙林校区)", dorm_type: "tag-dorm", ratio: "1:2.5 (绝对安全底牌)",
        pub_date: "2025-09-15", source: "南中医研招网", url: "http://gra.njucm.edu.cn/" 
    },

    // ===== 3. 江浙沪【强制 11408 预警梯队】(专硕提高门槛考数一+英一) =====
    { 
        name: "杭州电子科技大学", 
        major: "081200 计学 | 085404 计专 | 085405 软工",
        region: "江浙沪",
        cat: "double", tag: "tag-double", level: "双非IT神校 【专硕强制11408】", 
        subject: "11408 (数一+英一)",
        y2023: "318分 / 均348分", y2024: "326分 / 均355分", y2025: "324分 / 均352分",
        tuition: "8000 元/年", dorm: "保障校内宿舍 (约1200/年)", dorm_type: "tag-dorm", ratio: "1:6 (专硕考数一英一)",
        pub_date: "2025-09-19", source: "杭电研招目录", url: "http://yz.hdu.edu.cn/" 
    },
    { 
        name: "浙江工业大学", 
        major: "081200 计学 / 085400 计专",
        region: "江浙沪",
        cat: "double", tag: "tag-double", level: "浙江省属重点工科 【专硕强制11408】", 
        subject: "11408 (数一+英一)",
        y2023: "305分 / 均335分", y2024: "315分 / 均342分", y2025: "312分 / 均340分",
        tuition: "8000 元/年", dorm: "保障校内宿舍 (约1200/年)", dorm_type: "tag-dorm", ratio: "1:5 (专硕考数一英一)",
        pub_date: "2025-09-18", source: "浙工大研招网", url: "http://www.yz.zjut.edu.cn/" 
    },
    { 
        name: "南京航空航天大学", 
        major: "081200(11408) | 085404计专(11408)",
        region: "江浙沪",
        cat: "211", tag: "tag-211", level: "国防名门211 【专硕考数一英一】", 
        subject: "11408 (数一+英一)",
        y2023: "330分 / 均362分", y2024: "338分 / 均368分", y2025: "335分 / 均365分",
        tuition: "10000 元/年", dorm: "保障校内宿舍 (将军路校区)", dorm_type: "tag-dorm", ratio: "1:8 (竞争较强)",
        pub_date: "2025-09-16", source: "南航研招目录", url: "http://yz.nuaa.edu.cn/" 
    },
    { 
        name: "东南大学", 
        major: "081200 计学 / 085404 计专",
        region: "江浙沪",
        cat: "strong", tag: "tag-985", level: "江苏顶级985 【强制11408】", 
        subject: "11408 (数一+英一)",
        y2023: "342分 / 均368分", y2024: "350分 / 均374分", y2025: "346分 / 均371分",
        tuition: "10000 元/年", dorm: "保障校内宿舍 (九龙湖)", dorm_type: "tag-dorm", ratio: "1:8 (高难度)",
        pub_date: "2025-09-16", source: "东大研招目录", url: "http://yz.seu.edu.cn/" 
    },
    { 
        name: "同济大学", 
        major: "081200 计学 / 085404 计专",
        region: "江浙沪",
        cat: "strong", tag: "tag-985", level: "上海强势985 【强制11408】", 
        subject: "11408 (数一+英一)",
        y2023: "340分 / 均365分", y2024: "348分 / 均370分", y2025: "345分 / 均368分",
        tuition: "10000 元/年", dorm: "提供校内宿舍 (嘉定校区)", dorm_type: "tag-dorm", ratio: "1:7 (难度大)",
        pub_date: "2025-09-21", source: "同济研招网", url: "http://yz.tongji.edu.cn/" 
    },
    { 
        name: "浙江大学", 
        major: "081200 计学 / 085400 软件与计算机",
        region: "江浙沪",
        cat: "c9", tag: "tag-c9", level: "顶级985/C9 【强制11408】", 
        subject: "11408 (数一+英一)",
        y2023: "365分 / 均388分", y2024: "370分 / 均392分", y2025: "368分 / 均390分",
        tuition: "8000 (学硕) / 1.5万/年 (专硕)", dorm: "提供宿舍 (紫金港/玉泉)", dorm_type: "tag-dorm", ratio: "1:8 (神仙打架)",
        pub_date: "2025-09-18", source: "浙大研招目录", url: "http://yz.zju.edu.cn/" 
    },
    { 
        name: "复旦大学", 
        major: "081200 计学 / 085400 软件",
        region: "江浙沪",
        cat: "c9", tag: "tag-c9", level: "顶级985/C9 【强制11408+不保宿】", 
        subject: "11408 (数一+英一)",
        y2023: "355分 / 均382分", y2024: "360分 / 均385分", y2025: "358分 / 均384分",
        tuition: "10000 (学硕) / 4.0万/年 (专硕)", dorm: "❌ 专硕不提供校内宿舍 (租房高昂)", dorm_type: "tag-nodorm", ratio: "1:7 (成本极高)",
        pub_date: "2025-09-20", source: "复旦研招目录", url: "http://www.gs.fudan.edu.cn/" 
    },
    { 
        name: "中国科学技术大学", 
        major: "081200 计学 / 085400 计专",
        region: "安徽",
        cat: "c9", tag: "tag-c9", level: "顶级985/C9 【强制11408】", 
        subject: "11408 (数一+英一)",
        y2023: "360分 / 均385分", y2024: "365分 / 均388分", y2025: "362分 / 均386分",
        tuition: "8000 元/年", dorm: "保障校内宿舍", dorm_type: "tag-dorm", ratio: "1:6 (极难)",
        pub_date: "2025-09-15", source: "中科大研招网", url: "http://grs.ustc.edu.cn/" 
    },
    { 
        name: "北京邮电大学", 
        major: "081200 计学 / 085404 计专",
        region: "北京",
        cat: "strong", tag: "tag-211", level: "全国IT名门 【专硕考数一英一】", 
        subject: "11408 (数一+英一)",
        y2023: "335分 / 均365分", y2024: "345分 / 均372分", y2025: "342分 / 均370分",
        tuition: "10000 元/年", dorm: "提供宿舍 (沙河校区)", dorm_type: "tag-dorm", ratio: "1:10 (超热门)",
        pub_date: "2025-09-17", source: "北邮研招目录", url: "http://yz.bupt.edu.cn/" 
    },
    { 
        name: "西安电子科技大学", 
        major: "081200 计学 / 085404 计专",
        region: "陕西",
        cat: "strong", tag: "tag-211", level: "两电一邮/顶级211", 
        subject: "22408 (数二+英二)",
        y2023: "325分 / 均352分", y2024: "335分 / 均360分", y2025: "330分 / 均358分",
        tuition: "8000 元/年", dorm: "保障校内宿舍", dorm_type: "tag-dorm", ratio: "1:6 (适中偏难)",
        pub_date: "2025-09-18", source: "西电研招目录", url: "http://yz.xidian.edu.cn/" 
    },
    { 
        name: "深圳大学", 
        major: "081200 计学 / 085404 计专",
        region: "广东",
        cat: "double", tag: "tag-double", level: "特区双非强校/经费充足", 
        subject: "22408 (数二+英二)",
        y2023: "300分 / 均328分", y2024: "310分 / 均335分", y2025: "308分 / 均332分",
        tuition: "8000 元/年", dorm: "保障校内宿舍", dorm_type: "tag-dorm", ratio: "1:5 (适中)",
        pub_date: "2025-09-22", source: "深大研招网", url: "http://yz.szu.edu.cn/" 
    },
    { 
        name: "重庆邮电大学", 
        major: "081200 计学 / 085404 计专",
        region: "重庆",
        cat: "double", tag: "tag-double", level: "邮电特色双非/保底优选", 
        subject: "22408 (数二+英二)",
        y2023: "292分 / 均318分", y2024: "302分 / 均325分", y2025: "298分 / 均322分",
        tuition: "8000 元/年", dorm: "保障校内宿舍", dorm_type: "tag-dorm", ratio: "1:4 (稳妥保底)",
        pub_date: "2025-09-18", source: "重邮研招网", url: "http://yz.cqupt.edu.cn/" 
    }
];
