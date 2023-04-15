// ==UserScript==
// @name         Geek Dad Go - Procare data exporter for parents
// @namespace    everbird.gdg.exporter
// @license      MIT License
// @version      1.0
// @description  Export links of photos/videos along with there metadata into a CSV file. Once you have the links, you can use your preferred tool to download the photos and videos.
// @author       everbird
// @include      https://schools.procareconnect.com/*
// @require      https://code.jquery.com/jquery-3.6.0.min.js
// @grant        none
// ==/UserScript==

(function() {
    'use strict';

    const downloadPhotosBtn = $('<button>').text('Export photo links')
        .css({
            position: 'fixed',
            bottom: '20px',
            right: '20px',
            zIndex: '9999'
        });

    const downloadVideosBtn = $('<button>').text('Export video links')
        .css({
            position: 'fixed',
            bottom: '60px',
            right: '20px',
            zIndex: '9999'
        });

    function getToken() {
        var value = localStorage.getItem('persist:kinderlime');
        var tmp = JSON.parse(value);
        var user = JSON.parse(tmp.currentUser);
        var token = user.data.auth_token;
        return token;
    }

    function getPhotosUrl(dateString) {
        return 'https://api-school.kinderlime.com/api/web/parent/photos/?per_page=50&page=1&filters[photo][datetime_from]='+dateString+' 00:00&filters[photo][datetime_to]='+dateString+' 23:59';
    }

    function getVideosUrl(dateFrom, dateTo) {
        return 'https://api-school.kinderlime.com/api/web/parent/videos/?per_page=50&page=1&filters[video][datetime_from]='+dateFrom+' 00:00&filters[video][datetime_to]='+dateTo+' 23:59';
    }

    function fetch(url, token) {
        var xhr = new XMLHttpRequest();
        xhr.open('GET', url, false);
        xhr.setRequestHeader('Authorization', 'Bearer '+token);
        xhr.setRequestHeader('Content-Type', 'application/json');
        xhr.send();
        var r = JSON.parse(xhr.responseText);
        return r;
    }

    function convertToDateString(date) {
        var year = date.getFullYear();
        var month = date.getMonth() + 1;
        var day = date.getDate();
        var dateString = year + '-' + (month < 10 ? '0' + month : month) + '-' + (day < 10 ? '0' + day : day);
        return dateString;
    }

    function getPhotosBetween(datetime_from, datetime_to, token) {
        var fromDate = new Date(datetime_from)
        var utcFromDate = new Date(fromDate.getTime() + fromDate.getTimezoneOffset() * 60000);
        var toDate = new Date(datetime_to)
        var utcToDate = new Date(toDate.getTime() + toDate.getTimezoneOffset() * 60000);
        var currentDate = utcFromDate;
        
        var rs = [];
        while (currentDate <= utcToDate) {
            var currentDateString = convertToDateString(currentDate);
            console.info("Fetching photos for "+currentDateString);
            var url = getPhotosUrl(currentDateString);
            var result = fetch(url, token);
            rs.push(...result.photos);

            console.info("Current photos count:"+rs.length);
            currentDate.setDate(currentDate.getDate() + 1);
        }
        
        return rs;
    }

    downloadPhotosBtn.on('click', () => {
        var date_from = window.prompt("Please enter date from:");
        var date_to = window.prompt("Please enter date to:");
        
        var token = getToken();
        var photos = getPhotosBetween(date_from, date_to, token);
        var csv = photos.map(photo => `${photo.id},${photo.created_at},${photo.main_url}`).join('\n');

        var filename = 'procare-photos-csv-'+date_from+'_to_'+date_to+'.csv'
        var csvLinkContent = 'data:text/csv;charset=utf-8,' + csv;
        var encodedUri = encodeURI(csvLinkContent);
        var link = $('<a>').attr({
            href: encodedUri,
            download: filename
        }).appendTo('body');
        
        link.get(0).click();
        setTimeout(() => {
            link.remove();
        }, 0);
    });

    downloadVideosBtn.on('click', () => {
        var dateFrom = window.prompt("Please enter date from:");
        var dateTo = window.prompt("Please enter date to:");
        
        var token = getToken();
        var url = getVideosUrl(dateFrom, dateTo);
        var result = fetch(url, token);
        
        var csv = result.videos.map(v => `${v.id},${v.created_at},${v.video_file_url}`).join('\n');

        var filename = 'procare-videos-csv-'+dateFrom+'_to_'+dateTo+'.csv'
        var csvLinkContent = 'data:text/csv;charset=utf-8,' + csv;
        var encodedUri = encodeURI(csvLinkContent);
        var link = $('<a>').attr({
            href: encodedUri,
            download: filename
        }).appendTo('body');
        
        link.get(0).click();
        setTimeout(() => {
            link.remove();
        }, 0);
    });

    $('body').append(downloadPhotosBtn);
    $('body').append(downloadVideosBtn);
})();