package com.hcmanagement.controller;

import com.hcmanagement.service.DoctorExcelService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.*;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
public class DoctorReportController {
    
    @Autowired
    private DoctorExcelService doctorExcelService;

    @PostMapping("/generate/doctors/excel")
    public ResponseEntity<byte[]> generateDoctorsExcel(@RequestBody List<Map<String, Object>> doctors) throws Exception {
        byte[] excelBytes = doctorExcelService.generateDoctorsExcel(doctors);

        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_OCTET_STREAM);
        headers.setContentDisposition(ContentDisposition.attachment().filename("doctors.xlsx").build());

        return new ResponseEntity<>(excelBytes, headers, HttpStatus.OK);
    }

}
