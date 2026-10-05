/****************************************************************************************
  MASTER DO-FILE  |  Tahtia Sazwara MSc Thesis  |  Effect of Franchising Intensity on Performance
****************************************************************************************/

*** 0. House-keeping -------------------------------------------------------------
clear all
cd "/Users/sazwara/Documents/Class/MASTERS/MASTER THESIS/references"    // <-- adjust
capture mkdir tables
graph set window fontface "Cambria" /// omit this if there is no fontface


capture which reghdfe || ssc install reghdfe, replace
capture which ftools  || ssc install ftools,  replace
capture which estout || ssc install estout, replace
capture which utest || ssc install utest, replace

import excel "Thesis_Dataset_Clustered2.xlsx", sheet("Sheet1") firstrow clear //Adjust

*** 1. Data Cleaning -------------------------------------------------------------
rename ReturnonAssets roa
rename FRANCHISINGRATIO fratio
rename GlobalCompanyKey gvkey
rename OperatingProfitMarginAfterDe opm
rename NetProfitMargin npm
rename GrossProfitMargin gpm
rename InventoryTurnover inturn
rename ReceivablesTurnover recturn
rename AssetTurnover assturn
rename AvertisingExpensesSales avtsale
rename TotalDebtTotalAssets debtasset
rename TotalDebtEquity debtequi
rename QuickRatioAcidTest qratio
rename CurrentRatio cratio

gen fratio2 = fratio^2
gen fratio3 = fratio^3
gen double mdate = ym(Year , Month)        
format mdate %tm

label var roa      "Return on assets"
label var fratio   "F"
label var fratio2  "F²"
label var fratio3  "F³"
label var opm      "Operating profit margin"
label var npm      "Net profit margin"
label var gpm      "Gross profit margin"
label var assturn  "Asset turnover"
label var inturn	"Inventory Turnover"
label var recturn	"Receivables Turnover"
label var avtsale	"Advertising/Sales"
label var debtasset	"Debt/Asset"
label var debtequi "Debt/Equity"
label var qratio "Quick Ratio"
label var cratio "Current Ratio"

*** 2. Summary Statistics -------------------------------------------------------------
* 2.1. Store summary stats for whole varlist
estpost tabstat npm opm gpm roa debtasset debtequi qratio cratio inturn assturn recturn avtsale fratio AssetsTotal Age, ///
    stats(N count mean sd min max skewness kurtosis) columns(statistics)

* 2.2. Export as regression table
esttab . using "tables/Table_Summary.rtf",rtf replace title("Table 0. Descriptive Statistics") ///
    cells("count(fmt(a3)) mean(fmt(a3)) sd(fmt(a3)) min(fmt(a3)) max(fmt(a3)) skewness(fmt(a3)) kurtosis(fmt(%9.3f))") ///
    legend label nonumber noobs nogaps ///
    addnotes("Note: N = number of observations; SD = standard deviation.")
	
* 2.3. Summary statistics for categorical variable *
estpost tabstat fratio roa avtsale Age AssetsTotal, by(Cluster) ///
	statistics(count mean sd min max) columns(statistics) listwise

esttab . using "tables/Table_Summary_by_Cluster.rtf", rtf replace ///
    cells("count(fmt(a3)) mean(fmt(a3)) sd(fmt(a3)) min(fmt(a3)) max(fmt(a3))") ///
    legend label nonumber nonumber noobs nogaps ///
    title("Table 0.1. Descriptive Statistics by Clusters")
	

*** 3. First result -------------------------------------------------------------
eststo clear

*3.1. Run regressions and store in eststo
eststo M1, title([1]): reg roa fratio, r

eststo M2, title([2]): reg roa fratio fratio2, r

eststo M3, title([3]): reg roa fratio fratio2 fratio3, r

eststo M4, title([4]): reg roa fratio fratio2 i.Year, r

eststo M5, title([5]): reg roa fratio fratio2 i.Year i.gvkey, r

eststo M6, title([6]): reg roa fratio fratio2 fratio3 i.Year i.gvkey, r

* 3.2. Export as regression full table
esttab M1 M2 M3 M4 M5 M6 using "tables/Table_OLS.rtf",rtf replace title("Table 1. OLS regressions") ///
	cells(b(fmt(a3) star) se(par fmt(a3))) ///
	stats(r2_a N, fmt(a3) ///
	labels("Adjusted-R²" "N")) ///
	keep(fratio fratio2 fratio3 _cons) ///
	indicate("Year Dummy= *.Year" "Firm Dummy= *.gvkey") ///
	legend label collabels(none) nogaps noobs addnote("Note: Standard errors are in parentheses and robust to heteroskedasticity. Values are accordingly:")
	
*** 4. Second result -------------------------------------------------------------
xtset gvkey mdate

* 4.1. Run regressions and store in eststo
eststo X1, title([1]): reg roa fratio fratio2, vce(cluster gvkey)
eststo X2, title([2]): xtreg roa fratio fratio2, vce(cluster gvkey) 
eststo X3, title([3]): xtreg roa fratio fratio2 i.Year, fe vce(cluster gvkey)
eststo X4, title([4]): reghdfe roa fratio fratio2, absorb(gvkey Year) vce(cluster gvkey)

* 4.2. Export as regression table
esttab M2 X1 X2 X3 X4 using "tables/Table_FE_Comparison2.rtf",rtf replace  ///
	cells(b(fmt(a3) star) se(par fmt(a3))) ///
	stats(r2_a r2_w N, fmt(a3) ///
	labels("Adjusted-R²" "Within-R²"  "N")) ///
	keep(fratio fratio2 _cons) ///
	legend label collabels(none) nogaps eqlabels("OLS" "OLS" "XTREG" "XTREG" "REGHDFE", merge) noobs addnote("Note: Standard errors are in parentheses. Result is regressed against Return on Assets. Values are accordingly:")
	

* 4.3. Scatterplot visualization
qui xtreg roa fratio fratio2 i.Year, fe vce(cluster gvkey)
predict roahat, xb
twoway (scatter roa fratio, mcolor(gs8) msize(tiny)) ///
	(qfit roahat fratio) ///
	(lfit roahat fratio), ///
	legend(label(1 "Return on Assets") label(2 "Predicted quadratic") label(3 "Predicted linear")) title("Franchising Intensity vs. ROA")  xtitle("Franchising Intensity") ytitle("Return on Assets")


* 4.4. Keep most important models for main section, the rest goes to appendices


*** 5. Robustness test -------------------------------------------------------------
* 5.1. Store the robustness test models
eststo R1: quietly xtreg roa   fratio fratio2 i.Year, fe vce(cluster gvkey)
eststo R2: quietly xtreg opm   fratio fratio2 i.Year, fe vce(cluster gvkey)
eststo R3: quietly xtreg npm   fratio fratio2 i.Year, fe vce(cluster gvkey)
eststo R4: quietly xtreg gpm   fratio fratio2 i.Year, fe vce(cluster gvkey)
eststo R5: quietly xtreg inturn fratio fratio2 i.Year, fe vce(cluster gvkey)
eststo R6: quietly xtreg recturn fratio fratio2 i.Year, fe vce(cluster gvkey)
eststo R7: quietly xtreg assturn fratio fratio2 i.Year, fe vce(cluster gvkey)
eststo R8: quietly xtreg avtsale fratio fratio2 i.Year, fe vce(cluster gvkey)
eststo R9: quietly xtreg debtasset fratio fratio2 i.Year, fe vce(cluster gvkey)
eststo R10: quietly xtreg debtequi fratio fratio2 i.Year, fe vce(cluster gvkey)
eststo R11: quietly xtreg qratio fratio fratio2 i.Year, fe vce(cluster gvkey)
eststo R12: quietly xtreg cratio fratio fratio2 i.Year, fe vce(cluster gvkey)


* 5.2. Export to tables
esttab R1 R2 R3 R4 R5 R6 using "tables/Table_Robustness3.rtf",rtf replace ///
	mtitles("ROA" "Operating Margin" "Net Profit Margin" "Gross Profit Margin" "Inventory Turnover" "Receivables Turnover") ///
	cells(b(fmt(%9.3f) star) ///
	se(par fmt(%9.3f))) ///
	keep(fratio fratio2 _cons) ///
	stats(r2_a r2_w N, fmt(a3) labels("Adjusted-R²""Within-R²""N")) ///
	label nogaps noobs addnote("Note: Result based on panel data regression with XTREG, with firm and time fixed effect. Standard errors are in parentheses and clustered in firm level. Values are accordingly:")
	
esttab R7 R8 R9 R10 R11 R12 using "tables/Table_Robustness3.rtf",rtf append ///
	mtitles("Assets Turnover" "Advertising/Sales" "Debt/Assets" "Debt/Equity" "Quick Ratio" "Current Ratio") ///
	cells(b(fmt(%9.3f) star) ///
	se(par fmt(%9.3f))) ///
	keep(fratio fratio2 _cons) ///
	stats(r2_a r2_w N, fmt(a3) labels("Adjusted-R²""Within-R²""N")) ///
	label nogaps noobs addnote("Note: Result based on panel data regression with XTREG, with firm and time fixed effect. Standard errors are in parentheses and clustered in firm level. Values are accordingly:")

*** 6. Heterogeneity -------------------------------------------------------------
* 6.1. Store the four heterogeneity models
eststo H1: quietly xtreg roa fratio fratio2 i.SizeCatNum i.Year, fe vce(cluster gvkey)
eststo H2: quietly xtreg roa i.SizeCatNum##c.fratio fratio2 i.Year, fe vce(cluster gvkey)
eststo H3: quietly xtreg roa fratio fratio2 i.Cluster i.Year, fe vce(cluster gvkey)
eststo H4: quietly xtreg roa i.Cluster##c.fratio fratio2 i.Year, fe vce(cluster gvkey)

* 6.2. Export to tables
esttab H1 H2 using "tables/Table_Size.rtf",rtf replace ///
	mtitles("Size main-effects" "Size × Fratio" ) ///
	cells(b(fmt(%9.3f) star) se(par fmt(%9.3f))) ///
	keep(fratio fratio2 *.SizeCatNum#*.fratio _cons) ///
	indicate(Size Dummy=*.SizeCatNum) ///
	stats(r2_a r2_w N, fmt(a3) labels("Adjusted-R²" "Within-R² ""N")) ///
	label nogaps collabels(none) noobs addnote("Note: Result based on panel data regression with XTREG, with firm and time fixed effect. Standard errors are in parentheses and clustered in firm level. Values are accordingly:")

esttab H3 H4 using "tables/Table_Cluster.rtf",rtf replace ///
	mtitles( "Cluster main-effects" "Cluster × Fratio") ///
	cells(b(fmt(%9.3f) star) se(par fmt(%9.3f))) ///
	keep(fratio fratio2 *.Cluster#*.fratio _cons) ///
	stats(r2_a r2_w N, fmt(a3) labels("Adjusted-R²" "Within-R²" "N")) ///
	indicate(Cluster Dummy=*.Cluster) ///
	label nogaps collabels(none) noobs addnote("Note: Result based on panel data regression with XTREG, with firm and time fixed effect. Standard errors are in parentheses and clustered in firm level. Values are accordingly:")
	
** 6.2.1. Regression by each type
eststo C1: xtreg roa fratio fratio2 i.Year if Cluster==0, fe vce(cluster gvkey)
eststo C2: xtreg roa fratio fratio2 i.Year if Cluster==1, fe vce(cluster gvkey)
eststo C3: xtreg roa fratio fratio2 i.Year if Cluster==2, fe vce(cluster gvkey)
eststo C4: xtreg roa fratio fratio2 i.Year if Cluster==3, fe vce(cluster gvkey)

esttab C1 C2 C3 C4 using "tables/Table_types.rtf",rtf replace ///
	mtitles( "Established Giants""Steady Growth""Boutique Restaurants""Young & Lean") ///
	cells(b(fmt(%9.3f) star) se(par fmt(%9.3f))) ///
	keep(fratio fratio2  _cons) ///
	stats(r2_a r2_w N, fmt(a3) labels("Adjusted-R²" "Within-R²" "N")) ///
	label nogaps collabels(none) noobs addnote("Note: Result based on panel data regression with XTREG, with firm and time fixed effect. Standard errors are in parentheses and clustered in firm level. Values are accordingly:")
/*	
** 6.2.2. Compare xtreg and reghdfe for cluster
eststo H5: qui xtreg roa i.Cluster##c.fratio fratio2 i.Year, fe vce(cluster gvkey)
eststo H6: qui reghdfe roa i.Cluster##c.fratio fratio2, absorb(gvkey Year) vce(cluster gvkey)

esttab H5 H6 using "tables/Table_Cluster_XTREG.rtf",rtf replace ///
	mtitles( "Cluster main-effects" "Cluster × Fratio") ///
	cells(b(fmt(%9.3f) star) se(par fmt(%9.3f))) ///
	stats(r2_a r2_w N, fmt(a3) labels("Adjusted-R²" "Within-R²" "N")) ///
	indicate(Cluster Dummy=*.Cluster) ///
	label nogaps collabels(none) noobs addnote("Note: Result based on panel data regression with XTREG and REGHDFE, with firm and time fixed effect. Standard errors are in parentheses and clustered in firm level. Values are accordingly:")
*/

* 6.3. Visualization for cluster heterogeneity
qui reghdfe roa i.Cluster##c.fratio fratio2 , absorb(gvkey Year) vce(cluster gvkey)
qui predict clusterhat, xb
twoway (scatter roa fratio if Cluster==0, mcolor(gs8) msymbol(oh) msize(small)) ///
	(qfit clusterhat fratio if Cluster==0, sort lcolor(black)) ///
	(scatter roa fratio if Cluster==1, mcolor(gs10) msymbol(+) msize(small)) ///
	(qfit clusterhat fratio if Cluster==1, sort lcolor(navy)) ///
	(scatter roa fratio if Cluster==2, mcolor(gs12) msymbol(x) msize(small)) ///
	(qfit clusterhat fratio if Cluster==2, sort lcolor(green)) ///
	(scatter roa fratio if Cluster==3, mcolor(gs14) msymbol(dh) msize(small)) ///
	(qfit clusterhat fratio if Cluster==3, sort lcolor(maroon)), ///
	legend(label(1 "Established Giants" ) label(3 "Steady Growth") label(5 "Boutique Restaurants") ///
	label(7 "Young & Lean")) title("Franchising Intensity vs. ROA by Clusters")  ///
	xtitle("Franchising Intensity") ytitle("Return on Assets")

*** 7. Answer to empirical hypothesis -------------------------------------------------------------
qui /// 
	reg roa fratio fratio2, r       
	utest fratio fratio2 
	estadd scalar p1=r(p) 
	eststo U1  
qui ///
	xtreg roa fratio fratio2 i.Year, fe vce(cluster gvkey) 
	utest fratio fratio2 
	estadd scalar p1=r(p) 
	eststo U2  
qui ///
	reghdfe roa fratio fratio2, absorb(gvkey Year) vce(cluster gvkey) 
	utest fratio fratio2 
	estadd scalar p1=r(p) 
	eststo U3  

esttab U1 U2 U3 using "tables/Table_Ushape.rtf",rtf replace ///
    mtitles("OLS" "FE" "HDFE") ///
    keep(fratio fratio2) ///
    cells(b(fmt(%9.3f) star) se(par fmt(%9.3f))) ///
    stats(p1, fmt(%9.3f) labels("U-test P-value")) ///
    legend label noobs collabels(none) ///
    addnote("P-value for each model acquired from Lind & Mehlum (2010) U-test. SE in parentheses. Values are accordingly:") 

*** 8. Appendix: Full form tables -------------------------------------------------------------
esttab M1 M2 M3 M4 M5 M6 using "tables/Table_OLSfull.rtf",rtf replace title("Table 1. OLS regressions") ///
	cells(b(fmt(a3) star) se(par fmt(a3))) ///
	stats(r2_a N, fmt(a3) ///
	labels("Adjusted-R²" "N")) ///
	legend label collabels(none) nogaps noobs addnote("Note: Standard errors are in parentheses and robust to heteroskedasticity. Values are accordingly:")
	
esttab M2 X1 X2 X3 X4 using "tables/Table_FE_Comparison2full.rtf",rtf replace  ///
	cells(b(fmt(a3) star) se(par fmt(a3))) ///
	stats(r2_a r2_w N, fmt(a3) ///
	labels("Adjusted-R²" "Within-R²"  "N")) ///
	legend label collabels(none) nogaps eqlabels("OLS" "OLS" "XTREG" "XTREG" "REGHDFE", merge) noobs addnote("Note: Standard errors are in parentheses. Result is regressed against Return on Assets. Values are accordingly:")
	
esttab R1 R2 R3 R4 R5 R6 using "tables/Table_Robustness3full.rtf",rtf replace ///
	mtitles("ROA" "Operating Margin" "Net Profit Margin" "Gross Profit Margin" "Inventory Turnover" "Receivables Turnover") ///
	cells(b(fmt(%9.3f) star) ///
	se(par fmt(%9.3f))) ///
	stats(r2_a r2_w N, fmt(a3) labels("Adjusted-R²""Within-R²""N")) ///
	label nogaps noobs addnote("Note: Result based on panel data regression with XTREG, with firm and time fixed effect. Standard errors are in parentheses and clustered in firm level. Values are accordingly:")
	
esttab R7 R8 R9 R10 R11 R12 using "tables/Table_Robustness3full.rtf",rtf append ///
	mtitles("Assets Turnover" "Advertising/Sales" "Debt/Assets" "Debt/Equity" "Quick Ratio" "Current Ratio") ///
	cells(b(fmt(%9.3f) star) ///
	se(par fmt(%9.3f))) ///
	stats(r2_a r2_w N, fmt(a3) labels("Adjusted-R²""Within-R²""N")) ///
	label nogaps noobs addnote("Note: Result based on panel data regression with XTREG, with firm and time fixed effect. Standard errors are in parentheses and clustered in firm level. Values are accordingly:")
	
esttab H1 H2 using "tables/Table_Sizefull.rtf",rtf replace ///
	mtitles("Size main-effects" "Size × Fratio" ) ///
	cells(b(fmt(%9.3f) star) se(par fmt(%9.3f))) ///
	stats(r2_a r2_w N, fmt(a3) labels("Adjusted-R²" "Within-R² ""N")) ///
	label nogaps collabels(none) noobs addnote("Note: Result based on panel data regression with XTREG, with firm and time fixed effect. Standard errors are in parentheses and clustered in firm level. Values are accordingly:")

esttab H3 H4 using "tables/Table_Clusterfull.rtf",rtf replace ///
	mtitles( "Cluster main-effects" "Cluster × Fratio") ///
	cells(b(fmt(%9.3f) star) se(par fmt(%9.3f))) ///
	stats(r2_a r2_w N, fmt(a3) labels("Adjusted-R²" "Within-R²" "N")) ///
	label nogaps collabels(none) noobs addnote("Note: Result based on panel data regression with XTREG, with firm and time fixed effect. Standard errors are in parentheses and clustered in firm level. Values are accordingly:")
	