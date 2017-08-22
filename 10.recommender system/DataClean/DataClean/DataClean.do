clear all

*请把路径设置为与原始数据相同
*cd "/Users/VivianXU/Dropbox/Hackthon/Raw Data"


import excel using "FundationList_final.xls", firstrow clear


destring money, replace force
gen invest = money*10000
gen  user_f = regexm(user, "基金会$")
keep if user_f == 1

egen userid=group(user)
egen itemid= group(item)

drop if invest == .
drop if invest == 0
count
*3593
save "final_foundation_all",replace




*************************************
************invest times*************
*************************************
use "final_foundation_all", clear
duplicates report user item
duplicates tag user item, gen(invest_t)
sort user item
order user item invest_t
gen rate=invest_t+1
duplicates drop user item, force
keep user userid item itemid rate A
order user userid item itemid rate
count
*1323 after deduplication
export excel using "final_investtimes.xls", firstrow(var) replace
save "final_investtimes", replace
sum rate, detail
keep if rate >=10
export excel using "temp_investtimes10.xls", firstrow(var) replace



*************************************
************invest amount************
*************************************
import excel using "Foundation_asset_2013.xlsx", firstrow clear
ren name user
gen year = 2013
drop if asset == .
count
save "Foundation_asset_2013", replace

import excel using "Foundation_asset_2014.xlsx", firstrow clear
ren name user
gen year = 2014
destring asset, replace force
drop if asset == .
count
save "Foundation_asset_2014", replace

import excel using "Foundation_asset_2015.xlsx", firstrow clear
ren name user
gen year = 2015
destring asset, replace force
drop if asset == . 
count

append using "Foundation_asset_2013"
append using "Foundation_asset_2014"
count

gen asset2 = asset * 10000
drop asset
ren asset2 asset
save "Foundation_asset", replace





use "final_foundation_all", clear
merge m:1 user year using "Foundation_asset"
keep if _merge == 3
*10,663 matched with the asset info



*check the match result
*****
drop _merge
sum asset, detail
sum invest,detail
drop if asset <=0
gen rate2 = (invest/asset)*100

*****check
sum rate2, detail
sort user item year rate2 invest asset
order user item year rate2 invest asset
br if rate2>100



*******


*duplicates report user item
*duplicates tag user item, generate(dup)
sort user item year
by user item: egen rate3 = mean(rate2)

*by user item: gen total = sum(rate2[_n])

duplicates drop user item rate3, force
*duplicates report item
*sort item user
sum rate3, detail
keep user userid item itemid rate3
order user userid item itemid rate3
br if rate3 > 100
count
*927 after deduplication
export excel using "final_investamount.xls", firstrow(var) replace
save "final_investamount", replace




*********************
*******Rating********
*********************

********invest times*******
use "final_investtimes", clear
sum rate, detail
gen score_t = .
replace score_t = 31 if rate == 1
replace score_t = 31+3*(rate-1) if rate >1 
sum score_t, detail
save "rate_investtimes",replace





********invest amount*******
use "final_investamount", clear
tab rate3


preserve
keep if rate3< 0.01 | rate3 >=100
gen score_a = .
replace score_a = 5 if rate3< 0.01 
replace score_a = 100 if rate3>=100 
save "temp_tba", replace
restore


drop if rate3 < 0.01 | rate3 >=100
sum rate3, detail
centile rate3, centile(5 10 15 20 25)


_pctile rate3, nq(10)
gen score_a = . 
replace score_a = 10 if rate3<=r(r1)
replace score_a = 20 if rate3<=r(r2) & rate3>r(r1)
replace score_a = 30 if rate3<=r(r3) & rate3>r(r2)
replace score_a = 40 if rate3<=r(r4) & rate3>r(r3)
replace score_a = 50 if rate3<=r(r5) & rate3>r(r4)
replace score_a = 60 if rate3<=r(r6) & rate3>r(r5)
replace score_a = 70 if rate3<=r(r7) & rate3>r(r6)
replace score_a = 80 if rate3<=r(r8) & rate3>r(r7)
replace score_a = 90 if rate3<=r(r9) & rate3>r(r8)
replace score_a = 100 if rate3<=r(r10) & rate3>r(r9)

append using "temp_tba"
save "rate_investamount",replace




******merge*******
use "rate_investtimes", clear
merge 1:1 user item using "rate_investamount"  
keep if _merge == 3
drop A _merge
count
*1564
gen score_all = score_a*0.3 + score_t*0.7
ren rate rate_t
ren rate3 rate_a
export excel using "score_all.xls", firstrow(var) replace
save "score_all",replace











